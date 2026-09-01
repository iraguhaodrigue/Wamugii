import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { listUsers, type UserRead } from '@/api/users'

/** Shared id -> user lookup for STAFF/ADMIN screens (project client column, file uploader, etc). */
export function useUsersMap() {
  const query = useQuery({
    queryKey: ['users', 'all'],
    queryFn: listUsers,
    staleTime: 5 * 60 * 1000,
  })

  const usersMap = useMemo(() => {
    const map = new Map<number, UserRead>()
    query.data?.forEach((u) => map.set(u.id, u))
    return map
  }, [query.data])

  return {
    usersMap,
    users: query.data ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
  }
}
