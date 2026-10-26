## Searching Mosques

Mawaqit has no public search API, so the Mawaqit API can search mosques through a [SearXNG](https://docs.searxng.org/) instance. The search runs `site:mawaqit.net <your query>` and returns the mosques found, with the `masjid_id` (slug) you need for the other endpoints.

This feature is optional and disabled by default. Without it, the `/api/v1/search` endpoint returns `503 Service Unavailable`.

1. **Set up SearXNG:**

   - Run a SearXNG instance, for example with Docker:
     ```bash
     docker run -d --name searxng -p 8080:8080 searxng/searxng
     ```
   - Enable the `json` output format in the SearXNG `settings.yml`, otherwise SearXNG answers `403 Forbidden`:
     ```yaml
     search:
       formats:
         - html
         - json
     ```

2. **Configure the API:**

   - Set the `SEARXNG_URL` environment variable to the url of your SearXNG instance:
     ```env
     SEARXNG_URL=http://localhost:8080
     ```

3. **Search:**

   - **Request:**

     ```http
     GET /api/v1/search?q={name or city}&limit={1-50, default 10}
     ```

   - **Example:**

     ```http
     GET /api/v1/search?q=assalam argenteuil
     ```

   - **Result:**
     ```json
     [
       {
         "slug": "assalam-argenteuil",
         "name": "Mosquée Assalam - Argenteuil",
         "url": "https://mawaqit.net/fr/assalam-argenteuil"
       }
     ]
     ```

The results depend on the search engines configured in your SearXNG instance, so a mosque can be missing or the name can differ slightly from the one on mawaqit.net. When bearer token authentication is enabled, this endpoint requires the token like the other endpoints.
