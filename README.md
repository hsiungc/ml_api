<h1>Sentiment Analysis: End-to-End Machine Learning API</h1>

<h3>Overview</h3>

<p>This project is a complete deployment of a HuggingFace DistilBERT model API on Microsoft Azure. A FastAPI application was created to serve prediction results from user requests. Results were cached using Redis. Poetry was implemented to define application dependencies, and the application was tested using PyTest and GitHub Actions. The NLP application was then packaged using Docker, before deployed to Azure using Kubernetes (Minikube). Load testing was performed with K6, and results were visualized using Grafana to understand the dynamics of the system.
</p>

<p>The below assumes an Azure subscription is set up with Azure Kubernetes Service and Azure Container Repository.</p>

## Using the Application

Accessing the application requires curling the 'predict' endpoint with an example request:

> export NAMESPACE=hsiungc

> curl -X POST -H 'Content-Type: application/json' https://${NAMESPACE}.mids255.com/predict -d \
> '{"text": ["I love you", "I hate you", "Count to 1234"]}'

To view the application in a web browser, go to https://hsiungc.mids255.com/predict.

## Running the Test
To test the application, run the 'k6 run --summary-trend-stats="min,med,avg,max,p(99)" load.js' command.

Accessing the Grafana service requires port forwarding (kubectl port-forward -n prometheus svc/grafana 3000:3000). To view the Istio dashboards navigate to http://localhost:3000 in a web browser.

## Grafana Screenshots

Below are the screenshots taken from a K6 test run. The test was based on 10 virtual users (VUs) over the span of 10 minutes.

| ![alt text](https://github.com/UCB-W255/fall22-hsiungc/blob/main/final_project/grafana/_incoming_requests.png) |
|:---:|
| **Figure 1:** The incoming requests show 200 response codes. |

| ![alt text](https://github.com/UCB-W255/fall22-hsiungc/blob/main/final_project/grafana/_request_duration.png) |
|:---:|
| **Figure 2:** The max request duration at P(99) is around 1.10 seconds. |

| ![alt text](https://github.com/UCB-W255/fall22-hsiungc/blob/main/final_project/grafana/_request_size.png) |
|:---:|
| **Figure 3:** Request size remained even throughout testing. |

| ![alt text](https://github.com/UCB-W255/fall22-hsiungc/blob/main/final_project/grafana/_response_size.png) |
|:---:|
| **Figure 4:** Response size was relatively steady throughout testing. |

| ![alt text](https://github.com/UCB-W255/fall22-hsiungc/blob/main/final_project/grafana/_bytes_sent_received.png) |
|:---:|
| **Figure 5:** The number of bytes sent and received from Redis. |