NPM Dependency Network
######################

A python script that fetches an npm module and it's dependencies. 
Creates a graph on graphcommons.com and returns the url of created graph.

### Usage

```
$ python fetch.py --access_token=[YOUR_GRAPHCOMMONS_ACCESS_TOKEN] --depth=3 --package_name=react

Created Graph URL:
https://graphcommons.com/graphs/c8522ab2-35db-43c4-aa75-0b9de7280cba
```

### Options
```
  --access_token
      API Access to use Graph Commons API. You can get this token from 
      your profile page on graphcommons.com
      
  --package_name
      NPM package that will be fetched
      
  --depth
      Max depth of dependencies
```
