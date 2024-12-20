# API Documentation

## Endpoints

<details>
<summary>1. Get Logger</summary>

URL: `/api/logger/`  
Method: `GET`  
Description: Returns the current log level and logger name. Useful for debugging and monitoring the logging
configuration.**

Response Example:

```json
{
  "log_level": "INFO",
  "logger_name": "my_logger"
}
```

</details>

<details>
<summary>2. Get Tickers</summary>
**URL:** `/api/tickers/`  
**Method:** `GET`  
**Description:** **Retrieves a list of tickers.**  
**Query Parameters:**  
- `watcher` (optional): If `true`, returns watched tickers. Default is `true`.

**Response Example:**

```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc."
  },
  {
    "ticker": "GOOGL",
    "name": "Alphabet Inc."
  }
]
```

</details>

<details>
<summary>3. Get Watched List All</summary>

**URL:** `/api/watched-list/`  
**Method:** `GET`  
**Description:** **Retrieves the entire watched list of tickers.**

**Response Example:**

```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc."
  },
  {
    "ticker": "TSLA",
    "name": "Tesla Inc."
  }
]
```

</details>

<details>
<summary>4. Update Watch List</summary>

**URL:** `/api/watch-list/update/`  
**Method:** `POST`  
**Description:** **Updates the watch list with the provided tickers.**  
**Request Body:**

- `tickers` (list): List of tickers to update.

**Request Example:**

```json
{
  "tickers": ["AAPL",  "TSLA"]
}
```

**Response Example:**

```json
{
  "status": "success"
}
```

</details>

<details>
<summary>5. Add to Watch List</summary>

**URL:** `/api/watch-list/add/`  
**Method:** `POST`  
**Description:** **Adds tickers to the watch list.**  
**Request Body:**

- `tickers` (list): List of tickers to add.

**Request Example:**

```json
{
  "tickers": ["MSFT", "AMZN"]
}
```

**Response Example:**

```json
{
  "status": "success"
}
```

</details>

<details>
<summary>6. Remove from Watch List</summary>

**URL:** `/api/watch-list/remove/`  
**Method:** `POST`  
**Description:** **Removes tickers from the watch list.**  
**Request Body:**

- `tickers` (list): List of tickers to remove.

**Request Example:**

```json
{
  "tickers": ["AAPL"]
}
```

**Response Example:**

```json
{
  "status": "success"
}
```

</details>

<details>
<summary>7. Update Ticker List</summary>

**URL:** `/api/ticker-list/update/`  
**Method:** `POST`  
**Description:** **Updates the ticker list.**

**Response Example:**

```json
{
  "status": "Ticker list updated"
}
```

</details>

<details>
<summary>8. Store Ticker List</summary>

**URL:** `/api/ticker-list/store/`  
**Method:** `POST`  
**Description:** **Stores the provided ticker list.**  
**Request Body:**

- `tickers` (list): List of tickers to store.

**Request Example:**

```json
{
  "tickers": ["AAPL", "GOOGL", "TSLA"]
}
```

**Response Example:**

```json
{
  "status": "Ticker list stored"
}
```

</details>

<details>
<summary>9. Get All Tickers File</summary>

**URL:** `/api/tickers-file/`  
**Method:** `GET`  
**Description:** **Retrieves all tickers from the file.**

**Response Example:**

```json
[
  {
    
  "ticker": "AAPL", "name": "Apple Inc."},
  {
    
  "ticker": "GOOGL", "name": "Alphabet Inc."},
  {
    
  "ticker": "TSLA", "name": "Tesla Inc."}
]
```

</details>

<details>
<summary>10. Load Data</summary>

**URL:** `/api/data/load/`  
**Method:** `POST`  
**Description:** **Loads data for the provided tickers.**  
**Request Body:**

- `tickers` (list): List of tickers to load data for.

**Request Example:**

```json
{
  "tickers": ["AAPL", "GOOGL"]
}
```

**Response Example:**

```json
[
  {
    
  "ticker": "AAPL", "data": {"...":"..."}},
  {
    
  "ticker": "GOOGL", "data": {"...":"..."}}
]
```

</details>

<details>
<summary>11. Plot Graph</summary>

**URL:** `/api/graph/plot/`  
**Method:** `POST`  
**Description:** **Plots a graph for the provided data.**  
**Request Body:**

- `all_data` (list): Data to plot.
- `chunk_size` (optional): Size of data chunks. Default is `10`.

**Request Example:**

```json
{
  "all_data": [...],
"chunk_size": 10
}
```

**Response Example:**

```json
{
  "fig": "<html>...</html>"
}
```

</details>

<details>
<summary>12. Get Tickers from Variable</summary>

**URL:** `/api/tickers/variable/`  
**Method:** `GET`  
**Description:** **Retrieves tickers from a variable.**

**Response Example:**

```json
[
  {
    
  "ticker": "AAPL", "name": "Apple Inc."},
  {
    
  "ticker": "GOOGL", "name": "Alphabet Inc."}
]
```

</details>

<details>
<summary>13. Get Tickers from DB</summary>

**URL:** `/api/tickers/db/`  
**Method:** `GET`  
**Description:** **Retrieves tickers from the database.**

**Response Example:**

```json
[
  {
    
  "ticker": "AAPL", "name": "Apple Inc."},
  {
    
  "ticker": "GOOGL", "name": "Alphabet Inc."}
]
```

</details>