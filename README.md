# Application for the logistic and economic optimisation of car upgrades in Formula 1

Alessandro Russo

## Instructions for installing and using the application

- Fork the project at the following URL: https://github.com/TdP-prove-finali/RussoAlessandro
- Clone the project into your own development environment
- Install the dependencies by running: `pip install -r Requirements.txt`
- Create a local empty database named `f1_logistics_db` (MariaDB 10.10 or later)
- Import the database by running the file `f1_logistics_db.sql` in the `database` folder
- Update the database access data in the file `connector.cnf` (inside the `database` folder)
- Run the file `main.py` to start the application

## Configuration

- All the constants of the application are in the file `model/constants.py` and can be changed there:
  model parameters (α, β, logistic assumptions, default values, limit of 12 packages)
  and regulation values (ATR scale, cost caps, extra-race supplement), to be changed only if the regulations change
- Package costs, gains and lead times, circuit indices, rain probabilities and routes are in the database, not in `constants.py`
- The results reported in the thesis were obtained with the delivered values: changing the constants changes the results

The video showing how to use the software is available at the following YouTube link: [link to be added]

The road routes in the database are derived from data © OpenStreetMap contributors, ODbL licence.
