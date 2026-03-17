import os

# Example 1: Create directory
os.mkdir('new_folder')

# Example 2: Create nested directories
os.makedirs('parent/child', exist_ok=True)

# Example 3: List files
print(os.listdir('.'))

# Example 4: Check if directory exists
print(os.path.isdir('new_folder'))

# Example 5: Get current directory
print(os.getcwd())