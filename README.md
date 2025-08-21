# Med Machina

A medical robot directory. 

A simple site to track and sort medical robots, their capabilities, and their manufacturers.


See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### TODO Sprint 1
- ✔ add a disclaimer page : 
  - "the information on this site is provided as is, without any warranty or guarantee of accuracy. The site is not responsible for any errors or omissions in the information provided."
- ✔ separate companies from robots 2 separate pages
  - id as string
  - default is still the robots page
  - two separate datasets in the json file
- ✔ companies in the data order (json file)
- ✔ randomize the order of the robots on each display
- ✔ how to contribute page  
- RCM might stay as a tag specific values and others
- ✔ specify usage as an another tag cloud
- regulatory year and 
  - value like "FDA 2023" or "CE 2022" or "clinical trials" think enter the time interval (entering service and being retired) or "no certification"
  - in the data you can have a list of regulatory statuses
- description should allow html tags (or markdown) for formatting
- ✔ change the deguet brothers to "Aravind S. Kumar" "Anton Deguet" "Joris Deguet" 
- ✔ images as URL : ok 
- ✔ images catch exception if images have been removed
- ✔ search should find hits on description name and tags EVERYTHING
- ✔ companies show
  - name
  - list of robots
  - country
  - links (json array) if linkedin make it special
- ✔ contact us through the issues in the github repository

## TODO Sprint 2 (planning on Aug 18 2025)

- Change data structure for urls from an array of strings to an array of objects with a caption and a url
- Every link by URL should have a description from Json
- on robot detail, 
  - ajouter le nom de la company avant ou apres le nom du robot?  Par example: Intuitive: Ion ou Ion (Intuitive).  Dans l’ideal, le nom de la compagnie est un lien vers la page de detail de la companyX
  - remove every info on company cause we have a link to the company page
  - after description add titles for "Images from the web" and "Links" and "Tags"
  - double the image size
- on companies list, only name country and list of robots
- change title on home page to "Robots" instead of "A Medical Robot Directory"
- change the title of company detail to "Companies : <company name>" with Companies a link to company listing
- same for robots detail page "Robots : <robot name>" with Robots a link to robots listing
- Every link should look like a regular link in HTML, no button make it nice to look at
- In all listing for robots, keep the name, name of company, the first 5 tags (with ... if more)
- In all listing for companies, keep the name, country, and all robots   
- "search for a project..."  Remplacer par "Search..."
- Replace "Search for a company..." by "Search..."
- add a link to the bottom (common footer) to the disclaimer that makes it pop again
- Image link not clickable but add a way to open in a new tab, might be a hovering overlay or a link centered underneath
- description should allow html tags (or markdown) for formatting (leftover)
  
