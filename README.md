This repository contains my approach to solving the take-home test sent by orquest.

The premise of the exercise is intellectual property of orquest and will therefore not be reproduced here.

This solution consists of:
- A relational database (PostgreSQL)
- A web interface to said database (pgadmin)
- A data sample in csv format
- A small data pipeline to ingest the sample data into the database
- A dbt project to model the ingested data
- A metabase instance to showcase the result of the modeling

    ![Diagram](./diagram.png )


![Video follow-through](orquest_demo.mp4)


# Instructions

## 1. Dependencies
Ensure that `docker`, `docker compose` and `python3` are present in your system, as they will be required to evaluate the exercise. Additionally, we will need the `pip` package manager and the `venv` library.

```bash
docker --version
```
```bash
docker compose version
```
```bash
python3 --version
```
```bash
python3 pip --version
```
```bash
python -c "import venv" && echo "OK" || echo "NOK"
```

These commands should all return either the installed version of their respective programs, or the message "OK".

## 2. Virtual Environment
Enter the virtual environment.

Run the following commands from within this repo's main directory, according to your system:

   Linux/MacOS (untested):
   ```bash
   python3 -m venv orquest_env
   source ./orquest_env/bin/activate
   pip install -r requirements.txt
   export DBT_PROFILES_DIR="."
   ```

   Nix/NixOS:
   ```bash
   nix-shell
   ```

## 3. Spin up services
From within this repo's main directory, run
```bash
docker compose up -d
```
This will spin up the relational database, the web interface, the metabase instance, and will perform a data ingestion from the csv file into the database.

> Depending on your setup, you may need escalated privileges to run docker commands.

**NOTE:** Even though a dependency between the ingestion pipeline and the database container is established from within `docker-compose.yml`, the database signals readiness once the container is running, although the database may not necessairly be ready to accept connections. This may be the case depending on your system. A 45 second window is granted to the connection attempt before the pipeline gives up and crashes. If you observe that, after `docker compose up -d` has finished spinning up the containers, there is no `orquest_raw` schema in the database, a connection timeout has likely occured. You can verify this by running ` docker-compose logs ingest -f`, and verify that the waiting period elapsed betore a connection could be established. If that is the case, please run `docker compose up -d` once more, to retry the ingestion.


## 4. Log in the database web interface
Once all the containers are built and started, the web inferface can be accessed by visiting http://0.0.0.0:5050/login.
The user is **example@orquest.com** and the password is **password**.

After we log in, in order to be able to inspect our database, we will have to register it from the web interface. Since both the web interface and the database are within the same docker network, the hostname for the database is `my_db`. The full details are:
```
host: mydb
port: 5432
user: orquest
password: orquest
```
If the connection succeeds, we will be able to navigate to databases -> orquest_db -> schemas -> orquest_analytics, where our `invoices` table has been created. This is our raw data from the csv file.


**NOTE:** The `pgadmin` container will report to be running before it is ready to accept connections. If your browser returns an error when trying to access `pgadmin`, please run `docker-compose logs pgadmin -f` to check when the service is ready.


## 5. Log into Metabase
Metabase can be accessed via http://0.0.0.0:3000 .
The application database that Metabase uses is stored within this repository, so login details should not be required. Should they be needed at any stage, they are:
```
user: orquest@orquest.com
pw: orquest1
```

The models required by our visualization don't exist yet, so there isn't much for us to do here at the moment.

## 6. Execute the data modeling job
The dbt project responsible for the modeling of our source data is in the `orquest_dbt` directory. In order to materialize our models in the databse, we must run:

```bash
dbt run --project-dir orquest_dbt
```

## 7. Review results
Once our dbt job finishes, we can navigate back to Metabase -> _Our analytics_ collection. Here, we will find 2 assets. One (_MRR Bars_) is a visualization, and the other (_MRR Overview_ ) is a dashboard displaying said visualization. The results are best showcased by accessing the dashboard.

## 8. Deploy dbt documentation
Documentation about the models is included in the dbt project.
To review it, run:
```
dbt docs generate --project-dir orquest_dbt; dbt docs serve --project-dir orquest_dbt
```
A browser window will open at the address http://localhost:8080/#!/overview, through which the documentation can be explored.

## 9. Update source data
We can alter our source csv file and re-ingest it (the ingestion process will replace the table).
First, perform the desired changes in the file, and then execute `docker compose up -d`. All containers except the data ingestion should be already running, therefore we will simply cause the ingestion to execute again. Once that is done, we must run our modeling job again, as detailed on step 6.

## 10. Cleanup
When we decide that we are done with this exercise, our system can be cleaned up by running 
`docker-compose down --rmi all`. This will remove all images used by any service defined in this project.

Our relational database will have been created in the `analytics_db` directory. We can delete it with:
```bash
sudo rm ./analytics_db -rf
```
We need elevated privileges, since the owner of this directory is a user that does not exist outside our docker containers.

# RFC and design rationale
---
### Assumptions:
1. There is no 'grace period' for us to not consider a re-subscription as a reactivation (ie a user cancelling and re-subscribing the day after his previous subscription ended still constitutes a reactivation).
2. Upgrades and downgrades maintain their subscription_id.
3. Reactivations generate a new subscription_id.
4. Yearly subscripton amounts are not apportioned among the months within their validity period. Instead, their full amount is assigned to the month that the invoice was processed in.
5. There is a pre-existing relational model that contains dimensions such as users. There is no need to derive them from the `invoices` table.
6. Data is read from a data lake / replication has already been handled. Backing up the data falls out of scope.
7. If a change in billing_frecuency does not generate a new subscription_id, Monthly -> Anual will be considered an upgrade, and Anual -> Monthly a downgrade (becuse of Assumption 4). If the change does generate a new subscription_id, it will be considered a churn on the old subscription and a reactivation on the new one.
8. All users pay in the same currency, which is the one displayed in the table. No conversions or exchange rates need to be accounted for.


### Considered solutions:

I went back and forth with regards to the manner in which subscription continuity was to be established, in order to detect upgrades, downgrades, renewals, and churn. The current solution performs a self join, combining each subscription invoice with the one that preceded it, as long as their validity periods are consecutive. The same might have been accomplished by different techniques (such as window functions), which could prove to be computationally more efficient. On the other hand, performing a single self join instead of a window function for each of the columns to be derived allows for more readable code, and grants the ability to split the transformations across incremental, traceable steps.
In the end, given both the low volume and update frequency that is reasonable to be expected from a list of monthly and yearly invoices, and the impact that the ability of downstream analysts to understand the logic of the calculations can have on decision-making by the report consumers, I considered the tradeoff between performance and understandability more than justified.

In order to further ease understandability of the transformations by downstream analysts, I decided to split the incremental transformations among several dbt models. These models are configured as `ephemeral`, which means that they will not be materialized in the database, but dbt will instead aggregate them as CTEs at compile time, so there is no performance penalty against the database compared to sequential CTEs in a single model. The upside is that, by giving the ephemeral models a name that is descriptive of the transformation that takes place within them, documenting exclusively the columns that are generated or altered within them, and taking advantage of the fact that each ephemeral model still constitutes a node in the dbt dag, tracking transformations across the model lineage becomes trivial.

Another point of consideration was whether or not to apportion yearly subscriptions among the months within their validity period. One can see the utility in doing that, since in some scenarios the value generated by a subscription is better thought of as evenly distributed across the span of its validity. It stands to reason that (just like we don't consider that we work for our full salary on the first day of the month, and for free the rest of the time) in the scenario in which a customer pays N per year, we might be better served by thinking of this customer as paying N/12 each month. In other scenarios (such as VAT calculations), we would want to represent the full amount of the revenue generated by the company, regardless of its circumstances. Given the potential cost of erring on either side of this issue, and our lack of awareness of the stakeholder's preference, I decided to present data that is technically correct, even if it might produce some artifacts or fluctuations that could lend themselves to misinterpretation under certain use cases.

On the other hand, "spreading" the revenue evenly throughout a subscription's duration would allow us to report on a higher detail of granularity (we could even break it down per day), and would allow users to interpret the value of our current user base more intuitively. The logic to take this approach, however, becomes more convoluted, and the use cases that it enables fall out of the current scope. After some deliberation, I decided to opt for the _simpler_ approach of allocating the full amount of an invoice to the month when it was processed, since it covers our use case, can be quickly developed, it is straightforward to validate, and it can serve as a reference to check against in the future, should the need arise to pivot our design.

### Risks

The proposed solution is considered to be straightforward and quick to ship, but is also inflexible against a number of potential developments. Consider the following scenarios, and their consequences:
- Plans increase in price -> Every _existing_ subscription that was maintained through the price change will be considered an upgrade.
- We want to establish a period of time within a user can pay an invoice past the ending of their current subscription and still count it as _existing_ (otherwise every time a credit card expires and an invoice initially bounces, we are counting a churn). -> Self join no longer works, we must instead join on a date range, which span may vary and will require its own SCD.

Although the exercise explicitly states that they are not a factor, requirements change and refunds and trial periods may fall in scope in the future, but they would be trivial to account for. Extended time offers (such as 1 year + 3 months for free) would require no intervention.

### Next steps

At this stage we have a simple POC to bring forth to our stakeholders in order to gather feedback. It is a rare occurence when a stakeholder can produce an exhaustive list of requirements on the first try, so showing an early prototype will allow us to iterate quickly on our design with minimal effort wasted. Additionally, it gives us the chance to ask "_what should **always** be true_" about this data? Which requirements have we missed? Which new ones have they discovered after being in contact with the POC?

Regardless of the result of that process, there are a few aspects on which we could work:
- Testing: even at an early stage, there must be certain amount of ground work that can be done within a given testing framework.
- Orchestration: this models are now being manually ran in a development environment, but at some point in the future they will be merged and will have to fit in a greater data model. How and when will they get ran? Will they consume data from other models in the project? Will other models consume from them? This are important considerations in the context of dbt executions, where downstream dependencies or upstream consumers may be affected by the building of our models.
- Since the source `invoice` table is append only, our landing model could be transformed into an incremental model, and enriched with ingestion metadata (such as ingestion timestamp).
