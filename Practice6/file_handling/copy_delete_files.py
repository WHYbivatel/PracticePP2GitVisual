import shutil
import os

# Example 1: Copy file
shutil.copy('source.txt', 'copy.txt')

# Example 2: Copy file with metadata
shutil.copy2('source.txt', 'copy2.txt')

# Example 3: Delete file
if os.path.exists('copy.txt'):
    os.remove('copy.txt')

# Example 4: Delete directory
if os.path.exists('mydir'):
    shutil.rmtree('mydir')

# Example 5: Rename file
os.rename('copy2.txt', 'renamed.txt')