#mkdir folder name - makes a directory
#cd "folder names" = current working directory
# touch x.txt = creates a textfile
#git init - Initialized current repository
# cd ../ - takes back to parent directory
# git clone repository link - clones into local disk
# ls = all the files in the directory
# git status - to check whether a file has been modified
# cd .. - moves one directory back
#git add --all - makes changes so that u can commit into github repository
#git reset - removes all the changes
#git add . = changes in current working directory
# git rm file-name ---- removes the file
# git reset --hard file restored
# git rm folder name
# git rm -r folder name -- all the sub folders r also removed
# git log - all the commit
# branching - Makes sure the original file remains same all changes can be done and merged back
# git branch branch name - creates new branch name
# git checkout branch name - switches to that branch

# after committing reaches development stage so if u switch back to main branch, the file disappears
#git merge main -m "Merging main into development branch"

#git checking committing
#git checkout commit id - goes back to previous commit id
#git checkout main - Goes back to the latest commit

#Comparing between two different commits
# git diff first commit id then second commit id

#push - sending local changes to the remote(i.e github)
#fetch - bringing remote changes into local without merging
#pull - fetching plus merging

#git push origin "branch name" - pushing different branch
#git pull - pulls directly from github into local repository


#git stash - when u want to switch between branches without commit, allows to freely switch branches without the help of commit command .
#git stash pop - to make changes again

#git revert commit id  - used to undo commit then :wq to confirm the changes
