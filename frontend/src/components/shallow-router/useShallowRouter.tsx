import { useContext } from 'react'
import { ShallowRouterContext } from './shallow-router'

export const useShallowRouter = () => {
  const context = useContext(ShallowRouterContext)
  if (!context) {
    throw new Error('useShallowRouter must be used within a ShallowRouterProvider')
  }
  return context
}
