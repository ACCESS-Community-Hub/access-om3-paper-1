
Welcome to the documentation for the [_decoding-om3_](https://github.com/ACCESS-Community-Hub/decoding-om3) project! The purpose of this open source project is to encourage community users to delve inside the murky inner workings of om3.

Currently these topics are being explored as training as part of the regular Thursday 11:30 am COSIMA meetings being coordinated [here](https://docs.google.com/spreadsheets/d/1vk8m-oDRZChAFPnZ-HuF81YmiF7dkSXQkhZXekuj4fw/edit?gid=0#gid=0). Please get in touch with @chrisb13 (`chris.bull@anu.edu.au`) or @adele-morrison to get involved. Meetings are [announced on this thread](https://forum.access-hive.org.au/t/cosima-working-group-announce/238/181) and the [meeting link is this](https://utas.zoom.us/j/82678917036?from=addon).

A possible path forward from @AndyHoggANU and @chrisb13:
![Meeting notes](../assets/meeting1_AH-CB.jpg)

## Getting involved in _decoding-om3_

**Contributions from people of all career stages and backgrounds are highly encouraged.** All these models and configurations are developed are open source. Development is led by the [COSIMA working group](https://cosima.org.au/) and ACCESS-NRI and where we follow an open model.

Contributors so far include: Christopher Bull (ACCESS-NRI), Andy Hogg (ACCESS-NRI).

### Report a typo or make a suggestion

Technical issues related to _decoding-om3_  are best posted to [github.com/ACCESS-Community-Hub/decoding-om3/issues](https://github.com/ACCESS-Community-Hub/decoding-om3/issues). If you would like to discuss the issue first, feel free to post it on the [access hive forum](https://forum.access-hive.org.au/c/cosima/).

### _decoding-om3_ documentation

We appreciate contributions, typo and bugs fixes to this documentation. To make suggestions please see steps below.

#### Quick contributions 
!!! tip
    This method has the advantage is that it's *very quick* (<1 minute!). The caveat is that, unless you have write access to the `decoding-om3` repository, you will not be able to preview the changes rendered into a website or create whole new pages. <br>

The simplest and fastest way to make a change to an _existing_ page is to click the edit "pencil" on the top-right corner. This will go to the relevant GitHub markdown file and clicking the _top-right pencil again_ on GitHub will allow you to edit the file. Once complete, click `Commit changes...`. There are then _two_ possibilities, depending on whether you have  write access to [`decoding-om3`](https://github.com/ACCESS-Community-Hub/decoding-om3): 

1.  **No write access**: this will prompt you to make a fork and then a pull request (less than 1 minute!). 
1.  **You have write access**: please commit changes on a new branch and then use a pull request (this relates to the next option). 

#### Larger contributions (online PR-previews)
!!! tip
    This method allows you create whole new pages, and to preview the changes rendered into a website. It does not require you to install any software, but is **only available for people with write access to [`decoding-om3`](https://github.com/ACCESS-Community-Hub/decoding-om3)**.<br>

Create a new branch, e.g. `jblogs/doc-update`, make doc changes (the documentation sources are in [github.com/ACCESS-NRI/decoding-om3/tree/main/documentation](https://github.com/ACCESS-Community-Hub/decoding-om3/tree/main/documentation)), then open a related PR and a GitHub preview will be made automatically.

#### Larger contributions (`mkdocs` offline)
!!! tip
    Similar to the above, this method allows you create whole new pages and to preview the changes rendered into a website. It works whether or not you have write access to [`decoding-om3`](https://github.com/ACCESS-Community-Hub/decoding-om3), but requires you to install `mkdocs` and takes the longest to set up.<br>

Following [these instructions](https://docs.access-hive.org.au/about/contribute/#lets-get-started) but noting the documentation sources are in [github.com/ACCESS-Community-Hub/decoding-om3](https://github.com/ACCESS-Community-Hub/decoding-om3). You’ll need to fork the [ACCESS-Hive Docs GitHub repository](https://github.com/ACCESS-NRI/access-hive.org.au) and clone it locally if you want to write your own content. Once cloned, make sure to invoke `mkdocs serve` from within the `documentation` directory.

Additional steps and contribution guidelines can be found [here](https://docs.access-hive.org.au/about/contribute/#clone-the-forked-access-hive-docs-github-repository-locally).

If you want to add a new page, then you need to add another markdown file in the folder (or sub-folder as appropriate):
[github.com/ACCESS-NRI/decoding-om3/tree/main/documentation/docs/pages](https://github.com/ACCESS-Community-Hub/decoding-om3/tree/main/documentation/docs/pages)

Once done, update the documentation navigation in [github.com/ACCESS-NRI/decoding-om3/blob/main/documentation/mkdocs.yml](https://github.com/ACCESS-Community-Hub/decoding-om3/blob/main/documentation/mkdocs.yml) by adding an entry under the `nav:` section. Note you'll need to add the sub-folder paths as appropriate.




