# amerodi

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

### TODO 
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
- specify usage as an another tag cloud
- regulatory year and 
  - value like "FDA 2023" or "CE 2022" or "clinical trials" think enter the time interval (entering service and being retired) or "no certification"
  - in the data you can have a list of regulatory statuses
- description should allow html tags (or markdown) for formatting
- ✔ change the deguet brothers to "Aravind S. Kumar" "Anton Deguet" "Joris Deguet" 
- ✔ images as URL : ok 
- images catch exception if images have been removed
- ✔ search should find hits on description name and tags EVERYTHING
- ✔ companies show
  - name
  - list of robots
  - country
  - links (json array) if linkedin make it special
- ✔ contact us through the issues in the github repository
  
