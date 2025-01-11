## Required packages to run

-   `requests` module

## Using the script

1. Set the query keywords you want to use to search for. These work the same way as they do on the web version, so you can first test what keywords return papers of interest on https://arxiv.org/search/.
2. Configure the query settings. My use case is to find newest papers in the field, so I have sorted by descending date, showing the newest papers first. If you want to do bigger batches, arXiv allows up to 2000 entries. After that you'll need to modify the code to increment the start variable after every request to paginate the results.
3. Set the request delay. arXiv asks that you do not push requests to the API more often than every 3 seconds, however, for small batches, they seem to tolerate no delays. If you receive a response 503, that means that you have sent too many requests too quickly; allow for some time to pass before trying again.
4. Set the filter keywords. Only papers that have at least one of these keywords in the title or abstract will be kept.
5. Set the date offset. The integer value specifies how many days from today should be considered.
6. Set the output filename.
7. Run and receive the markdown summary of the retrieved papers.

---

Thank you to arXiv for use of its open access interoperability.
