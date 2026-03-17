import shutil

# Example 1: Move file
shutil.move('file.txt', 'new_folder/file.txt')

# Example 2: Rename using move
shutil.move('new_folder/file.txt', 'new_folder/new_name.txt')

# Example 3: Move directory
shutil.move('parent', 'moved_parent')

# Example 4: Move with overwrite handling
if not os.path.exists('dest.txt'):
    shutil.move('source.txt', 'dest.txt')

# Example 5: Move multiple files
files = ['a.txt', 'b.txt']
for f in files:
    shutil.move(f, 'new_folder/')
