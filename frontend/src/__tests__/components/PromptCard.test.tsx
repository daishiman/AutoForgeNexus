// Example unit test for PromptCard component
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { render } from '../test-utils/render'
import { createMockPrompt } from '../factories/prompt.factory'
import { PromptCard } from '@/components/prompts/PromptCard'

// Mock useRouter
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe('PromptCard', () => {
  const mockPrompt = createMockPrompt({
    id: '1',
    title: 'Test Prompt',
    content: 'This is a test prompt content',
    tags: ['test', 'example'],
    isPublic: true,
  })

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render prompt title and content', () => {
      render(<PromptCard prompt={mockPrompt} />)

      expect(screen.getByText('Test Prompt')).toBeInTheDocument()
      expect(screen.getByText('This is a test prompt content')).toBeInTheDocument()
    })

    it('should render all tags', () => {
      render(<PromptCard prompt={mockPrompt} />)

      expect(screen.getByText('test')).toBeInTheDocument()
      expect(screen.getByText('example')).toBeInTheDocument()
    })

    it('should show public badge for public prompts', () => {
      render(<PromptCard prompt={mockPrompt} />)

      expect(screen.getByText('Public')).toBeInTheDocument()
    })

    it('should show private badge for private prompts', () => {
      const privatePrompt = createMockPrompt({ isPublic: false })
      render(<PromptCard prompt={privatePrompt} />)

      expect(screen.getByText('Private')).toBeInTheDocument()
    })

    it('should truncate long content', () => {
      const longPrompt = createMockPrompt({
        content: 'A'.repeat(200),
      })
      render(<PromptCard prompt={longPrompt} />)

      const content = screen.getByTestId('prompt-content')
      expect(content.textContent?.length).toBeLessThan(200)
    })
  })

  describe('Interactions', () => {
    it('should navigate to prompt detail on click', async () => {
      render(<PromptCard prompt={mockPrompt} />)

      const card = screen.getByTestId('prompt-card')
      fireEvent.click(card)

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith(`/prompts/${mockPrompt.id}`)
      })
    })

    it('should handle edit action', async () => {
      const onEdit = jest.fn()
      render(<PromptCard prompt={mockPrompt} onEdit={onEdit} />)

      const editButton = screen.getByLabelText('Edit prompt')
      fireEvent.click(editButton)

      expect(onEdit).toHaveBeenCalledWith(mockPrompt)
    })

    it('should handle delete action with confirmation', async () => {
      const onDelete = jest.fn()
      window.confirm = jest.fn(() => true)

      render(<PromptCard prompt={mockPrompt} onDelete={onDelete} />)

      const deleteButton = screen.getByLabelText('Delete prompt')
      fireEvent.click(deleteButton)

      expect(window.confirm).toHaveBeenCalledWith(
        'Are you sure you want to delete this prompt?'
      )
      expect(onDelete).toHaveBeenCalledWith(mockPrompt.id)
    })

    it('should not delete when confirmation is cancelled', async () => {
      const onDelete = jest.fn()
      window.confirm = jest.fn(() => false)

      render(<PromptCard prompt={mockPrompt} onDelete={onDelete} />)

      const deleteButton = screen.getByLabelText('Delete prompt')
      fireEvent.click(deleteButton)

      expect(onDelete).not.toHaveBeenCalled()
    })

    it('should handle like action', async () => {
      const onLike = jest.fn()
      render(<PromptCard prompt={mockPrompt} onLike={onLike} />)

      const likeButton = screen.getByLabelText('Like prompt')
      fireEvent.click(likeButton)

      expect(onLike).toHaveBeenCalledWith(mockPrompt.id)
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<PromptCard prompt={mockPrompt} />)

      expect(screen.getByRole('article')).toHaveAttribute(
        'aria-label',
        `Prompt: ${mockPrompt.title}`
      )
    })

    it('should support keyboard navigation', async () => {
      render(<PromptCard prompt={mockPrompt} />)

      const card = screen.getByTestId('prompt-card')
      card.focus()

      expect(card).toHaveFocus()

      fireEvent.keyDown(card, { key: 'Enter' })

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith(`/prompts/${mockPrompt.id}`)
      })
    })

    it('should have proper heading hierarchy', () => {
      render(<PromptCard prompt={mockPrompt} />)

      const heading = screen.getByRole('heading', { level: 3 })
      expect(heading).toHaveTextContent(mockPrompt.title)
    })
  })

  describe('Loading States', () => {
    it('should show loading state when actions are pending', async () => {
      const onDelete = jest.fn(() => new Promise(resolve => setTimeout(resolve, 100)))
      window.confirm = jest.fn(() => true)

      render(<PromptCard prompt={mockPrompt} onDelete={onDelete} />)

      const deleteButton = screen.getByLabelText('Delete prompt')
      fireEvent.click(deleteButton)

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()

      await waitFor(() => {
        expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
      })
    })
  })

  describe('Error States', () => {
    it('should handle delete errors gracefully', async () => {
      const onDelete = jest.fn(() => Promise.reject(new Error('Delete failed')))
      window.confirm = jest.fn(() => true)

      render(<PromptCard prompt={mockPrompt} onDelete={onDelete} />)

      const deleteButton = screen.getByLabelText('Delete prompt')
      fireEvent.click(deleteButton)

      await waitFor(() => {
        expect(screen.getByText('Failed to delete prompt')).toBeInTheDocument()
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle prompt without tags', () => {
      const promptWithoutTags = createMockPrompt({ tags: [] })
      render(<PromptCard prompt={promptWithoutTags} />)

      expect(screen.queryByTestId('tag-list')).toBeEmptyDOMElement()
    })

    it('should handle very long titles', () => {
      const longTitlePrompt = createMockPrompt({
        title: 'A'.repeat(100),
      })
      render(<PromptCard prompt={longTitlePrompt} />)

      const title = screen.getByTestId('prompt-title')
      expect(title).toHaveClass('truncate')
    })

    it('should handle missing description', () => {
      const promptWithoutDescription = createMockPrompt({ description: undefined })
      render(<PromptCard prompt={promptWithoutDescription} />)

      expect(screen.queryByTestId('prompt-description')).not.toBeInTheDocument()
    })
  })
})