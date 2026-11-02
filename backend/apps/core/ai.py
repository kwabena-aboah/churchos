import logging

import anthropic
import openai
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from apps.finance.models import Transaction, TransactionType
from apps.members.models import Member, MemberStatus
from .models import ChurchSettings

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o-mini",
}


class AIProviderError(Exception):
    pass


def get_ai_api_key(provider, church=None):
    if church is None:
        church = ChurchSettings.get_cached()

    church_key = getattr(church, f"ai_{provider}_api_key")
    environment_key = getattr(settings, f"{provider.upper()}_API_KEY", "")
    return church_key or environment_key


def get_configured_provider(church):
    if church.ai_provider == "built_in":
        return "built_in"

    providers = (
        ("anthropic", "openai")
        if church.ai_provider == "auto"
        else (church.ai_provider,)
    )
    for provider in providers:
        if get_ai_api_key(provider, church):
            return provider
    return "built_in"


def _church_context(church):
    today = timezone.localdate()
    month_transactions = Transaction.objects.filter(
        is_active=True,
        transaction_date__year=today.year,
        transaction_date__month=today.month,
    )
    income_types = [
        TransactionType.TITHE,
        TransactionType.OFFERING,
        TransactionType.DONATION,
        TransactionType.PLEDGE_PAYMENT,
        TransactionType.HALL_RENTAL,
        TransactionType.OTHER_INCOME,
    ]
    income = month_transactions.filter(
        transaction_type__in=income_types
    ).aggregate(total=Sum("amount"))["total"] or 0
    expenses = month_transactions.filter(
        transaction_type=TransactionType.EXPENSE
    ).aggregate(total=Sum("amount"))["total"] or 0
    members = Member.objects.filter(
        is_active=True,
        membership_status=MemberStatus.ACTIVE,
    ).count()

    return {
        "church": church.church_name,
        "date": today.isoformat(),
        "active_members": members,
        "currency": church.currency_symbol,
        "month": today.strftime("%B %Y"),
        "income": float(income),
        "expenses": float(expenses),
    }


def _built_in_response(message, context):
    question = message.lower()
    response_lines = [
        f"I'm the built-in ChurchOS assistant for {context['church']}.",
    ]

    if any(word in question for word in ("finance", "income", "giving", "tithe", "offering", "expense")):
        response_lines.extend([
            f"For {context['month']}, recorded income is "
            f"{context['currency']}{context['income']:,.2f} and recorded expenses are "
            f"{context['currency']}{context['expenses']:,.2f}.",
            "These figures summarize recorded transactions and are not a forecast.",
        ])
    elif any(word in question for word in ("member", "membership", "people", "congregation")):
        response_lines.append(
            f"There are {context['active_members']:,} active members currently recorded."
        )
    elif any(word in question for word in ("hello", "hi", "hey", "good morning", "good afternoon")):
        response_lines.append(
            f"Today is {context['date']}. I can help with basic questions about current "
            "membership and this month's recorded finances."
        )
    else:
        response_lines.extend([
            f"I can currently reference {context['active_members']:,} active members and "
            f"this month's recorded income ({context['currency']}{context['income']:,.2f}) "
            f"and expenses ({context['currency']}{context['expenses']:,.2f}).",
            "For generated summaries and broader questions, configure an Anthropic or "
            "OpenAI API key in Settings → Integrations & AI.",
        ])

    return "\n\n".join(response_lines)


def generate_ai_response(church, messages):
    provider = get_configured_provider(church)
    if provider == "built_in":
        context = _church_context(church)
        return _built_in_response(messages[-1]["content"], context), provider

    api_key = get_ai_api_key(provider, church)
    model = getattr(church, f"ai_{provider}_model") or DEFAULT_MODELS[provider]
    context = _church_context(church)
    system_prompt = (
        f"You are a concise, pastoral church management assistant for {context['church']}. "
        f"Today is {context['date']}. You may use these aggregate figures: "
        f"{context['active_members']} active members; for {context['month']}, "
        f"income {context['currency']}{context['income']:,.2f} and expenses "
        f"{context['currency']}{context['expenses']:,.2f}. These figures are recorded "
        "totals, not forecasts. Do not claim access to individual member records. "
        "Be warm, professional, and concise."
    )

    try:
        if provider == "anthropic":
            response = anthropic.Anthropic(api_key=api_key).messages.create(
                model=model,
                max_tokens=1000,
                system=system_prompt,
                messages=messages,
            )
            reply = response.content[0].text
        else:
            response = openai.OpenAI(api_key=api_key).chat.completions.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages,
                ],
            )
            reply = response.choices[0].message.content or ""
    except anthropic.APIError as exc:
        raise AIProviderError("The configured AI provider request failed.") from exc
    except openai.APIError as exc:
        raise AIProviderError("The configured AI provider request failed.") from exc

    return reply, provider
