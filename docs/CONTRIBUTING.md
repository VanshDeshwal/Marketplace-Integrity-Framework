# 🤝 Contributing Guide

## Welcome Contributors!

Thank you for your interest in contributing to the Marketplace Integrity Framework! This guide will help you get started with contributing to our project.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Contribution Workflow](#-contribution-workflow)
- [Coding Standards](#-coding-standards)
- [Testing Guidelines](#-testing-guidelines)
- [Documentation](#-documentation)
- [Community](#-community)

---

## 🤖 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race
- Ethnicity
- Age
- Religion
- Nationality

### Expected Behavior

- **Be respectful** and constructive in all interactions
- **Be collaborative** and help others learn
- **Be inclusive** and welcoming to newcomers
- **Give credit** where credit is due
- **Focus on** what's best for the community

### Unacceptable Behavior

- Harassment, discrimination, or offensive language
- Personal attacks or trolling
- Sharing private information without consent
- Spam or irrelevant promotional content

---

## 🚀 Getting Started

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug reports and fixes**
- ✨ **New features and enhancements**
- 📚 **Documentation improvements**
- 🧪 **Test coverage improvements**
- 🎨 **UI/UX improvements**
- 🔧 **Performance optimizations**
- 🌐 **Translations and localization**

### Before You Start

1. **Search existing issues** to avoid duplicates
2. **Check the roadmap** to align with project direction
3. **Join our Discord** to discuss your ideas
4. **Review recent PRs** to understand current development patterns

---

## 💻 Development Setup

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Git** 2.20+
- **Docker** 20.10+ (optional)
- **VS Code** (recommended)

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/Marketplace-Integrity-Framework.git
cd Marketplace-Integrity-Framework

# Add upstream remote
git remote add upstream https://github.com/VanshDeshwal/Marketplace-Integrity-Framework.git
```

### Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Frontend Setup

```bash
cd frontend
npm install

# Install additional development tools
npm install --save-dev @testing-library/jest-dom
npm install --save-dev eslint-config-prettier
```

### Environment Configuration

Create `.env` files:

**Backend `.env`**:
```bash
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000
DEVELOPMENT=true
```

**Frontend `.env`**:
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

### Verify Setup

```bash
# Test backend
cd backend
python -c "from app.main import app; print('✅ Backend setup successful')"

# Test frontend
cd frontend
npm test -- --watchAll=false
```

---

## 🔄 Contribution Workflow

### 1. Create an Issue

Before starting work, create or find an issue:

```markdown
## Bug Report / Feature Request

**Description**
Clear description of the bug or feature

**Steps to Reproduce** (for bugs)
1. Step one
2. Step two
3. Expected vs actual behavior

**Proposed Solution** (for features)
Detailed description of the proposed implementation

**Additional Context**
Screenshots, logs, or other relevant information
```

### 2. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Make Changes

Follow these principles:
- **Small, focused commits** with clear messages
- **Test your changes** thoroughly
- **Update documentation** as needed
- **Follow coding standards** (see below)

### 4. Commit Guidelines

Use conventional commit format:

```bash
git commit -m "type(scope): description"

# Examples:
git commit -m "feat(api): add fraud detection endpoint"
git commit -m "fix(ui): resolve duplicate detection layout issue"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(backend): add unit tests for image processing"
```

**Commit Types**:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 5. Push and Create PR

```bash
# Push your branch
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Use the PR template and fill in all sections
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] New tests added (if applicable)

## Checklist
- [ ] Code follows project standards
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #123
```

---

## 📏 Coding Standards

### Python (Backend)

#### Style Guide
We follow **PEP 8** with some modifications:

```python
# Use Black formatter (line length: 88)
# Use isort for import sorting
# Use flake8 for linting

# Good examples:
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ProductAnalyzer:
    """Analyzes products for duplicates and fraud."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.model = None
    
    async def analyze_image(
        self, 
        image_data: bytes, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Analyze image for similar products.
        
        Args:
            image_data: Raw image bytes
            top_k: Number of results to return
            
        Returns:
            List of similar products with scores
            
        Raises:
            ValueError: If image_data is invalid
        """
        if not image_data:
            raise ValueError("Image data cannot be empty")
            
        logger.info(f"Analyzing image, returning top {top_k} results")
        return await self._process_image(image_data, top_k)
```

#### Key Principles
- **Type hints** for all function parameters and returns
- **Docstrings** for all public functions and classes
- **Error handling** with specific exception types
- **Logging** instead of print statements
- **Async/await** for I/O operations

#### Pre-commit Configuration

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

### JavaScript/React (Frontend)

#### Style Guide
We use **Prettier** and **ESLint** with React best practices:

```javascript
// Use functional components with hooks
import React, { useState, useEffect, useCallback } from 'react';
import { Upload, AlertCircle, CheckCircle } from 'lucide-react';
import { toast } from '../hooks/useToast';

/**
 * Component for duplicate detection functionality
 */
const DuplicateDetection = ({ onResults, onError }) => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Use useCallback for event handlers
  const handleFileUpload = useCallback(async (file) => {
    if (!file) {
      onError('Please select a file');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/dedup/image', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      onResults(data.results);
      toast.success(`Found ${data.results.length} similar products`);
    } catch (error) {
      console.error('Upload failed:', error);
      onError(error.message);
    } finally {
      setIsLoading(false);
    }
  }, [onResults, onError]);

  return (
    <div className="duplicate-detection">
      <div className="upload-area">
        <Upload size={48} />
        <p>Drag & drop an image or click to browse</p>
      </div>
    </div>
  );
};

export default DuplicateDetection;
```

#### Key Principles
- **Functional components** with hooks
- **PropTypes** or TypeScript for type checking
- **Meaningful component names** in PascalCase
- **Custom hooks** for reusable logic
- **Error boundaries** for error handling
- **Accessibility** attributes (aria-label, role, etc.)

#### ESLint Configuration

`.eslintrc.js`:
```javascript
module.exports = {
  extends: [
    'react-app',
    'react-app/jest',
    'prettier'
  ],
  plugins: ['react-hooks'],
  rules: {
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'no-unused-vars': 'warn',
    'no-console': 'warn'
  }
};
```

---

## 🧪 Testing Guidelines

### Backend Testing

#### Unit Tests with pytest

```python
import pytest
from unittest.mock import Mock, patch
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

class TestDuplicateDetection:
    """Test cases for duplicate detection endpoints."""
    
    def test_health_check(self):
        """Test health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
    
    @patch('app.main.IMG_MODEL')
    def test_image_upload_success(self, mock_model):
        """Test successful image upload and processing."""
        # Mock the model response
        mock_model.encode_image.return_value = Mock()
        
        # Prepare test image
        test_image = b"fake_image_data"
        files = {"file": ("test.jpg", test_image, "image/jpeg")}
        
        response = client.post("/dedup/image", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_image_upload_invalid_file(self):
        """Test upload with invalid file type."""
        files = {"file": ("test.txt", b"not_an_image", "text/plain")}
        response = client.post("/dedup/image", files=files)
        assert response.status_code == 400

# Integration tests
class TestIntegration:
    """Integration tests for full workflows."""
    
    @pytest.mark.asyncio
    async def test_full_duplicate_detection_workflow(self):
        """Test complete duplicate detection process."""
        # This would test the entire pipeline
        pass

# Test fixtures
@pytest.fixture
def sample_image():
    """Provide sample image for testing."""
    return b"sample_image_bytes"

@pytest.fixture
def mock_faiss_index():
    """Mock FAISS index for testing."""
    with patch('app.main.ART') as mock_art:
        mock_art.get.return_value = Mock()
        yield mock_art
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"
```

### Frontend Testing

#### Unit Tests with Jest and React Testing Library

```javascript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DuplicateDetection from '../components/DuplicateDetection';

// Mock fetch
global.fetch = jest.fn();

describe('DuplicateDetection', () => {
  const mockOnResults = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders upload area', () => {
    render(
      <DuplicateDetection 
        onResults={mockOnResults} 
        onError={mockOnError} 
      />
    );
    
    expect(screen.getByText(/drag & drop/i)).toBeInTheDocument();
  });

  test('handles file upload successfully', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({ results: [{ id: 1, score: 0.95 }] }),
    };
    fetch.mockResolvedValueOnce(mockResponse);

    render(
      <DuplicateDetection 
        onResults={mockOnResults} 
        onError={mockOnError} 
      />
    );

    const file = new File(['hello'], 'hello.jpg', { type: 'image/jpeg' });
    const input = screen.getByLabelText(/upload/i);
    
    await userEvent.upload(input, file);
    
    await waitFor(() => {
      expect(mockOnResults).toHaveBeenCalledWith([{ id: 1, score: 0.95 }]);
    });
  });

  test('handles upload error', async () => {
    fetch.mockRejectedValueOnce(new Error('Upload failed'));

    render(
      <DuplicateDetection 
        onResults={mockOnResults} 
        onError={mockOnError} 
      />
    );

    const file = new File(['hello'], 'hello.jpg', { type: 'image/jpeg' });
    const input = screen.getByLabelText(/upload/i);
    
    await userEvent.upload(input, file);
    
    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Upload failed');
    });
  });
});

// Integration tests
describe('DuplicateDetection Integration', () => {
  test('complete user workflow', async () => {
    // Test the entire user journey
    const user = userEvent.setup();
    
    render(<App />);
    
    // Navigate to duplicate detection
    await user.click(screen.getByRole('tab', { name: /duplicate/i }));
    
    // Upload file
    const file = new File(['image'], 'test.jpg', { type: 'image/jpeg' });
    const input = screen.getByLabelText(/upload/i);
    await user.upload(input, file);
    
    // Verify results display
    await waitFor(() => {
      expect(screen.getByText(/results/i)).toBeInTheDocument();
    });
  });
});
```

#### Test Coverage Requirements

- **Minimum 80%** overall coverage
- **90%+ for critical paths** (API endpoints, core logic)
- **100% for utility functions**

```bash
# Run tests with coverage
npm test -- --coverage --watchAll=false

# Coverage thresholds in package.json
{
  "jest": {
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

---

## 📚 Documentation

### Code Documentation

#### Python Docstrings
Use **Google style** docstrings:

```python
def process_image(image_data: bytes, model_config: Dict[str, Any]) -> List[float]:
    """Process image and extract feature embeddings.
    
    This function takes raw image data, preprocesses it according to the model
    requirements, and extracts feature embeddings using the loaded vision model.
    
    Args:
        image_data: Raw image bytes in supported format (JPEG, PNG, WebP).
        model_config: Configuration dictionary containing model parameters.
            Expected keys:
                - 'input_size': Tuple of (width, height) for image resizing
                - 'normalize': Boolean indicating whether to normalize inputs
                - 'device': Device to run inference on ('cpu' or 'cuda')
    
    Returns:
        List of float values representing the image embedding vector.
        Length depends on the model architecture (typically 512 or 768 dimensions).
    
    Raises:
        ValueError: If image_data is empty or invalid format.
        RuntimeError: If model is not loaded or inference fails.
        
    Example:
        >>> with open('product.jpg', 'rb') as f:
        ...     image_data = f.read()
        >>> config = {'input_size': (224, 224), 'normalize': True, 'device': 'cpu'}
        >>> embeddings = process_image(image_data, config)
        >>> len(embeddings)
        512
    """
```

#### JavaScript JSDoc
```javascript
/**
 * Handles file upload and duplicate detection
 * @param {File} file - The image file to analyze
 * @param {Object} options - Configuration options
 * @param {number} options.topK - Number of results to return
 * @param {number} options.threshold - Similarity threshold (0-1)
 * @returns {Promise<Array>} Array of similar products
 * @throws {Error} When file is invalid or API request fails
 * 
 * @example
 * const results = await handleFileUpload(file, { topK: 10, threshold: 0.8 });
 * console.log(`Found ${results.length} similar products`);
 */
async function handleFileUpload(file, options = {}) {
  // Implementation
}
```

### Writing User Documentation

#### Structure
- **Overview** - What the feature does
- **Prerequisites** - What users need
- **Step-by-step instructions** - How to use it
- **Examples** - Real-world usage
- **Troubleshooting** - Common issues
- **FAQ** - Frequently asked questions

#### Style Guidelines
- Use **active voice** ("Click the button" not "The button should be clicked")
- **Short paragraphs** (2-3 sentences max)
- **Bullet points** for lists
- **Code blocks** for technical content
- **Screenshots** for UI features
- **Consistent terminology** throughout

---

## 🎯 Review Process

### Pull Request Reviews

#### What Reviewers Look For

1. **Functionality**
   - Does the code work as intended?
   - Are edge cases handled?
   - Is error handling appropriate?

2. **Code Quality**
   - Is the code readable and maintainable?
   - Are naming conventions followed?
   - Is the code properly structured?

3. **Performance**
   - Are there any performance bottlenecks?
   - Is memory usage reasonable?
   - Are database queries optimized?

4. **Security**
   - Are inputs properly validated?
   - Are there any security vulnerabilities?
   - Is sensitive data handled correctly?

5. **Testing**
   - Are tests comprehensive?
   - Do tests cover edge cases?
   - Is test coverage sufficient?

#### Review Checklist

**For Authors**:
- [ ] Self-reviewed the code
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] CI/CD passes
- [ ] Breaking changes documented

**For Reviewers**:
- [ ] Code functionality verified
- [ ] Code style consistent
- [ ] Tests comprehensive
- [ ] Documentation adequate
- [ ] Security considerations addressed
- [ ] Performance implications considered

### Review Etiquette

#### Giving Feedback
- **Be constructive** - Suggest improvements, don't just point out problems
- **Be specific** - Reference exact lines and provide examples
- **Explain reasoning** - Help others learn from your feedback
- **Acknowledge good work** - Highlight positive aspects

Example good review comments:
```
// Good: Constructive with suggestion
Consider using a more descriptive variable name here. Instead of `data`, 
maybe `product_metadata` would be clearer?

// Good: Educational
This approach works, but we could improve performance by using a dictionary 
lookup instead of a linear search. Here's an example: [code snippet]

// Good: Acknowledging good work
Nice job handling the edge case where the image might be corrupted! 
The error message is very helpful for debugging.
```

#### Receiving Feedback
- **Be open-minded** - Consider all feedback thoughtfully
- **Ask questions** - If something isn't clear, ask for clarification
- **Say thank you** - Appreciate the time reviewers spend
- **Learn from feedback** - Use reviews as learning opportunities

---

## 🏆 Recognition

### Contributor Levels

#### New Contributor
- First PR merged
- Added to contributors list
- Welcome package (stickers, documentation access)

#### Regular Contributor
- 5+ PRs merged
- Helped with code reviews
- Access to contributor Discord channel

#### Core Contributor
- 20+ PRs merged
- Significant feature contributions
- Mentoring new contributors
- Repository triage permissions

#### Maintainer
- Long-term commitment to project
- Technical leadership
- Full repository access
- Decision-making authority

### Hall of Fame

We maintain a hall of fame for outstanding contributors:

```markdown
## 🌟 Hall of Fame

### 🏆 Top Contributors (2025)
- **@contributor1** - 47 PRs, fraud detection system
- **@contributor2** - 23 PRs, React UI overhaul
- **@contributor3** - 31 PRs, performance optimizations

### 🎯 Special Recognition
- **Best First PR**: @newbie - comprehensive docs update
- **Most Helpful**: @mentor - helped 12 new contributors
- **Innovation Award**: @researcher - novel ML approach
```

---

## 📞 Getting Help

### Communication Channels

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/VanshDeshwal/Marketplace-Integrity-Framework/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/VanshDeshwal/Marketplace-Integrity-Framework/discussions)
- **💬 Community Chat**: [Discord Server](https://discord.gg/marketplace-integrity)
- **📧 Private Questions**: [Email maintainers](mailto:maintainers@marketplace-integrity.com)

### Office Hours

Core maintainers host weekly office hours:
- **When**: Fridays, 2-3 PM UTC
- **Where**: Discord voice channel
- **Topics**: Questions, architecture discussions, roadmap planning

### Mentorship Program

New contributors can request mentorship:
- Paired with experienced contributor
- Weekly 30-minute check-ins
- Help with first 3 PRs
- Introduction to codebase and processes

---

## 🎉 Thank You!

Your contributions make this project better for everyone. Whether you're fixing typos, adding features, or helping other contributors, every contribution matters.

Remember:
- **Start small** - Small contributions are valuable and welcome
- **Be patient** - Good software takes time to build
- **Have fun** - Enjoy the process of learning and building together
- **Ask questions** - We're here to help you succeed

Happy coding! 🚀
