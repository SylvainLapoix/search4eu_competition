# Memorious crawler : EU competition

Memorious crawler for the EU competition portal.

## Setup

```shell
# set up the service
docker-compose up -d
# crawl:
# - access the memorious CLI
docker-compose run --rm worker /bin/sh
# - see available crawlers
memorious list
# - run a crawler : antitrust and cartels
memorious run competition_1
```
