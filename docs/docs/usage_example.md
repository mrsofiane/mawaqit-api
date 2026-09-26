## Usage Examples

In the following examples, the mosque ID used is `assalam-argenteuil`.

To demonstrate how to use the Mawaqit API, here are some usage examples:

Replace `{masjid_id}` with the ID of the mosque you're interested in. You can find the mosque ID on the [Mawaqit website](https://mawaqit.net).

The full API documentation is available at `localhost:8000/docs`.

1. **Retrieve Prayer Times for a Specific Mosque:**

- **Request:**

  ```http
  GET /api/v1/{masjid_id}/prayer-times
  ```

- **Example:**

  ```http
  GET /api/v1/assalam-argenteuil/prayer-times
  ```

- **Result:**
  ```json
  {
    "fajr": "05:31",
    "sunrise": "06:45",
    "dohr": "13:02",
    "asr": "16:22",
    "maghreb": "19:13",
    "icha": "20:24"
  }
  ```

2.  **Retrieve Month Calendar of Prayer Times:**

    - **Request:**

      ```http
      GET /api/v1/{masjid_id}/calendar/{month_number}
      ```

    - **Example:**

      ```http
      GET /api/v1/assalam-argenteuil/calendar/5
      ```

- **Result:**

  ```json
  [
    {
      "fajr": "05:04",
      "sunrise": "06:30",
      "dohr": "13:53",
      "asr": "17:48",
      "maghreb": "21:10",
      "icha": "22:33"
    },
    {
     ...
    },
    {
      "fajr": "04:10",
      "sunrise": "05:52",
      "dohr": "13:53",
      "asr": "18:03",
      "maghreb": "21:48",
      "icha": "23:28"
    }
  ]
  ```

These examples demonstrate how to use the Mawaqit API endpoints to retrieve prayer times data for specific mosques, calendars for the year and month, etc. Adjust the `{masjid_id}` and `{month_number}` placeholders with the actual IDs and numbers as needed.

3. **Subscribe to the Prayer Calendar (iCalendar / `.ics`):**

   Calendar apps such as Apple Calendar and Google Calendar can subscribe to a feed URL. The feed returns RFC 5545 content (`text/calendar`).

   - **Adhan (athan) times:**

     ```http
     GET /api/v1/{masjid_id}/calendar.ics
     ```

   - **Iqama times:**

     ```http
     GET /api/v1/{masjid_id}/calendar-iqama.ics
     ```

   - **Optional query parameters:**

     | Parameter | Default | Description |
     |-----------|---------|-------------|
     | `duration` | `15` | Event length in minutes (`1`–`180`) |
     | `include_shuruk` | `false` | Include Shuruk/sunrise events (adhan feed only) |
     | `token` | — | Bearer token as query param when `ENABLE_AUTH=true` (calendar clients cannot send auth headers) |

   - **Example subscribe URL:**

     ```http
     GET /api/v1/assalam-argenteuil/calendar.ics?duration=10&include_shuruk=true
     ```

   - **Response headers:** `Content-Type: text/calendar; charset=utf-8`, `Content-Disposition: inline; filename="{masjid_id}.ics"`, `Cache-Control: public, max-age=3600`.
