# How to use Github and exoset

## Github Administrator
invite a collaborator (use email address or look for the account in the search bar):
    
1. on the webpage of the repository (https://github.com/admin_user/repository_name/settings) select 
‘Collaborators’ in the left side menu
2. confirm password
3. use the green button “add people”, search the person by github username or full name or email, select the desired 
user and invite to collaborate. This operation send an email to the user

## PULL-REQUEST

As administrator you must check / accept the pull requests made by your collaborators.

If you want to ask for changes, you want to add a comment you must do it from github webpage, otherwise you can simply
go on exoset webpage, access to the restricted access and you will be redirected to the list of the pending pull requests 
that have passed the check runs.
The administrator can check the details of the pull request and merge it (by clicking on merge) if the pull request can be 
merged. 
By clicking on "merge" the pull request is approved and the upstream is automatically updated as well as exoset web-plateform. 
If a new exercise has been added, this new exercise will appear in “List of the exercises only on Github” in exoset 
admin web-plateform (https://exoset.epfl.ch/admin_github/list_resources_files), if the exercise has been changed please open it to generate the new pdf.

## Collaborator
#### Step one: create a Github account
(if you have one already please skip this step and go 
to the next one)

Go on github.com, click on sign up follow the instructions and login

### Step two: set up your environment

Confirm the invitation you have received by email, if you didn't ask again to the
Github administrator

Open the repository (https://github.com/admin_user/repository_name/) and fork it (use the menu on the top left). 
This action will create a clone repository under your account so the repository where you will work will be redirected 
to:

https://github.com/YOUR_USERNAME/repository_name/

### Step three: start working on latex files

Sometimes you can work directly on github website, this is recommended only when you have to do small 
changes (like correcting a spelling error). In these cases go to your github repository page and:
  
1. **Click on fetch upstream → fetch and merge** (your repository will be updated with the main  repository)
2. select the file you want to change
3. on the top right of the file click on pencil icon
4. modify the file with the GitHub text editor
5. scroll down and make your comment for the commit
6. click on Commit changes 

Although it is highly recommended to work on your local machine to to so you need to need to setup your local environ:

- clone the repository on your machine and set up upstream:

 1. in terminal go to the directory you want to work
 2. write the following command line:
    
    `git clone https://github.com/YOUR_USERNAME/repository_name.git`
    
    if you are using a personal access token or use this if you use ssh authentication:
    
    `git clone git@github.com:YOUR_USERNAME/repository_name.git`
    
 3. wait until all the files are copied in the folder
 4. verify that the origin with the following command line (access token and ssh have different urls...):
 
    `git remote -v` 
    
    you should get the following answer:
    
    `origin git@github.com:YOUR_USERNAME/repository_name .git (fetch)`
    `origin git@github.com:YOUR_USERNAME/repository_name .git (push)`
    
 5. now we need to set the upstream (to catch all the changes and synchronize with the main 
 repository  admin_user/repository_name). To do so:
 
     `git remote add upstream https://github.com/admin_user/repository_name/`
     
     verify origin and upstream with 4.
 
 6. before making any change on the files in the repository please remember to update the repository you work on:
 
    `git pull upstream master`
    `git fetch upstream master`
    
    if you see that some commit have been updates run the following command (skip this if the message "Already up to 
    date is shown")
    
    `git push origin master`

 Now your local repository and your remote are up to date with the upstream, you can start working, **please work exercise 
 by exercise, don’t push plenty**:
 
 - work with your latex editor on the files and please **verify that the file compile without error**
 - make your commit (appendix)
 - push your changes to your repository
 
    `git push`
    
Now you are ready for the pull request. Keep in mind to make a pull request per exercise, this will 
simply your life in case of CONFLICTS. Also verify that the exercise compile and the pdf does not contains errors.

If you have partial modification that you do not want to submit please create a different branch, when these 
modifications are acceptable you can merge this branch with you master.

### PULL-REQUEST: how to
 
On GitHub repository page (the one you have forked it – url https://github.com/YOUR_USERNAME/repository_name.git )

- select the menu « Pull request » → click on new pull request. A screen which compares the changes is shown, 
you can see the list of your commits, which files have been changed  
- Click on « Create pull request » verify your comment and confirm clicking on « Create pull request »
- doing so you will be redirected to the administrator repository and verify the status (only the administrator can 
validate and merge your changes in the main repository). After few minutes you can check if your code have passed the 
test, if so a green check is shown. 
Still review required and merging is blocked (action done by the administrator) if you get a red flag is because 
your files contains error ( i.e. the name of the files is not correct, latex files does not compile). 
In this case make the appropriate change until you will get a green flag. If everything is correct then you should 
contact the administrator.
-  Once the pull request pass the test the administrator will receive an email

    - Administrator can leave a comment. The comment is shown automatically under your own comment. This is just a comment
    - Administrator can ask for change, you can change the files / add comment, the administrator will see what you have 
    done. Checks re-runs automatically
    - Administrator can accept your pull request as it is from exoset web-platform
- Once the PR is approved, your modifications will be merged in the administrator repository and all the collaborators can 
pull your work.


	 
## MAKE a COMMIT:

verify the status of your local repository:

> `git status`

you will have a list of existing files that have been changed (“Changes not staged for commit:”) and new files (“Untracked files:”)
add the files you need with 

> `git add list_of_the_files`

now you are ready for a commit

> `git commit -m “message_of_your_commit”`

## Connect via ssh to github

### Windows

Create ssh key :

1. first check if already exists, open windows terminal and type

> `ls -al ~/.ssh`

if this command shows some files like these :

> id_rsa.pub
> id_ecdsa.pub
> id_ed25519.pub

it means you already have one and you can copy it with the following
command line :
> `clip < ~/.ssh/id…..whateveryouhavefilename.pub`

and go to step 3 else go to 2
2. if you don not have any ssh-key you need to create one, do not worry, it is easy and
painful type the following command line

> `ssh-keygen -t ed25519 -C "your_email_ sur_github @example.com "`

When you're prompted to "Enter a file in which to save the key," press Enter.
This accepts the default file location.
At the prompt, type a secure passphrase. Just press enter (twice, cause it will
ask to repeat the password). When finished copy the contents of your key by typing :
3. copy the key
> `clip < ~/.ssh/id_ed25519.pub`

### Mac / Linux 

1.check for existing ssh key:

> `cat ~/.ssh/` use tab to see if suggestions are prompted 

or 

> `cat /Users/USERNAME/.ssh/` use tab to see if suggestions are prompted

if a pair exists jump to step 3 otherwise generate a new one with step 2
2.open a terminal and type:

> `ssh-keygen -t rsa`

the terminal will prompt some questions, name and password, leave them empty, of course if you already have one key do 
not overwrite it 
3. copy the key

> `pbcopy < ~/.ssh/whatevernameyougivetoyourfile.pub`


4. include the sshkey in your github account (this will avoid typing username and password when you communicate with origin)
To do so go to your account settings on Github, choose "SSH and GPG keys" from the left menu, click on add ssh key,
give a name in title section and paste your key in key section and save it.



    
     
