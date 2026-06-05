# Cluj Buses
A little Python application that simulates buses going round and round using Apache Kafka. Currently, the bus routes are from Cluj-Napoca, Romania. The buses do not stop.

The buses send notifications of their states to a Kafka topic. The information is processed using [Quix Streams](https://github.com/quixio/quix-streams), displayed to console and forwarded to other topics.

## Implemented continuous queries:
  - Select overcrowded buses
  - Select buses reaching their next stop in less than a number of meters
  - Select slow buses (buses that did not reach their next stop within a time limit)

## Requirements:
- docker/docker-compose 
- Python 3.9+ (note: application has been run with 3.14)


> [!NOTE]
> In case the installation of **quixstreams** gives a gcc error, either install missing gcc/g++/make libraries or librdkafka, if the system is not among the ones supported by the library developers (Windows, MacOS, Ubuntu etc., more information on their website)

## How to run:
Use the following commands in the folder where the docker-compose.yml file is accessible.

### Step 0 - Build the cluster

```console
docker compose build
```
Only necessary once.

### Step 1 - Start the Kafka cluster

```console
docker compose up -d
```
This will start the containers in detached mode (simply put, you dont see all the logs in the terminal).

### Step 2 - Run the consumers
The project contains ```consumers.py``` where each query pipeline is assigned to a separate consumer group and application, and ```consumers-branched.py``` where the branching feature is used to execute operations in parallel. Multithreading has not been attempted due to lack of resources. Try at your own risk.

In the terminal use this command, make sure you are in the Python environment. 
```console
python [filename]
```

### Step 3 - Run the producer
The file ```producer.py``` contains the main notification logic. While every bus is responsible for updating its state when requested, the main runner resides in this file and moves the buses one step every ```TICK_INTERVAL```

```console
python producer.py
```

The producer and consumers can be ran in any order because the consumers will process all the messages since the last checkpoint. However, in this order the output makes more sense. 

### Step 4 - Stop the processes
Simply use CTRL-C (or its equivalents) to send a ```KeyboardInterrupt``` which will stop the producer or consumer(s). 

To stop the cluster use the following command:
```console
docker compose down
```
Optional parameter "-v" to remove volumes.

> [!TIP]
> After modifying the topology of the consumers, the program might break with a message about checkpoints.
> 
> Fix: change the consumer group.

## Resources:
- Theoretical information provided in the pdf
- **Cluster** docker compose file and additional information can be found in the [Quix Docs](https://quix.io/docs/quix-streams/tutorials/index.html#running-kafka-locally)



---

###### Proof of concept motivated by the frustration of bus notification boards not alerting arrivals properly. Uploaded on a whim so the repository does not follow upload conventions.
