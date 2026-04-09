import { ref, computed } from 'vue'

export function usePagination(loadFn) {
  const pagination = ref({ count: 0, total_pages: 1, current_page: 1, next: null, previous: null })

  const pageNumbers = computed(() => {
    const pages = []
    const total = pagination.value.total_pages
    const cur = pagination.value.current_page
    const start = Math.max(1, cur - 2)
    const end = Math.min(total, cur + 2)
    for (let i = start; i <= end; i++) pages.push(i)
    return pages
  })

  function setPagination(data) {
    if (data.count !== undefined) {
      pagination.value = {
        count: data.count,
        total_pages: data.total_pages || 1,
        current_page: data.current_page || 1,
        next: data.next,
        previous: data.previous,
      }
    }
  }

  function goPage(page) {
    if (page >= 1 && page <= pagination.value.total_pages) {
      loadFn(page)
    }
  }

  return { pagination, pageNumbers, setPagination, goPage }
}
