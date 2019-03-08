## cgccli
CLI tool for CGC Public API. 

### CGC
The Cancer Genomics Cloud (CGC), powered by Seven Bridges, is one of three pilot systems funded by the National Cancer 
Institute to explore the paradigm of colocalizing massive genomics datasets, like The Cancer Genomics Atlas (TCGA), 
alongside secure and scalable computational resources to analyze them.
___

### Installation
>-Note: This guide is for UNIX-like systems, but it should also work for Windows with some changes

##### Pip installation

You can install `cgccli` inside virtual environment so it won't pollute your global environment. In that 
case command will only be available if virtual environment is activated(prerequisites: `pip` and/or `virtualenv` 
or similar)
    
```bash
virtualenv .env
source .env/bin/activate
pip install cgccli
```
>-Note: First two lines are optional.

##### Manual installation
1) Pull project from GitHub
2) Navigate to project directory
3) Run installation
    
    ```bash
    virtualenv .env
    source .env/bin/activate
    pip install --editable .
    ```
    >-Note: First two lines are optional. Last command might require `sudo` privileges.
        
4) Test package installation by running 
    ```bash
    cgccli --help
    ```

5) Congrats! You are all set! 

___

### Usage
#### Getting started
It is suggested that you start with
```bash
cgccli --help
```
and browse from there.

#### Sample usage
```bash
cgccli --token {token} projects list
cgccli --token {token} files list --project
test/simons-genome-diversity-project-sgdp
cgccli --token {token} files stat --file {file_id}
cgccli --token {token} files update --file {file_id} name=bla
cgccli --token {token} files update --file {file_id}
metadata.sample_id=asdasf
cgccli --token {token} files download --file {file_id} --dest
/tmp/foo.bar
```
>-Note that command params with whitespaces in keys or values should be surrounded by quotation marks
>```bash
>cgccli --token {token} files update --file {file_id} "metadata.some field=blah blah"
>or
>cgccli --token {token} files update --file {file_id} metadata.sample_id="value with whitespace"
>```
#### Config
TODO

___

### Coming soon
- Config settings for UNIX-like and Windows systems
- Refactor (moving commands to classes instead of callback functions for easier implementation of new sub-commands)
- 


