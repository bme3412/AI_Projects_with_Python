function populateYears(ticker) {
    const yearDropdown = document.querySelector('select[name="year"]');
    fetch(`/get-10k-filings?ticker=${ticker}`)
        .then(response => response.json())
        .then(data => {
            console.log(data); // Log the API response for debugging
            yearDropdown.innerHTML = ''; // Clear existing options
            filingsByYear = {}; // Reset the filingsByYear object

            if (Array.isArray(data) && data.length) {
                data.forEach(filing => {
                    const year = new Date(filing.fillingDate).getFullYear();
                    filingsByYear[year] = filing; // Store the filing by year

                    if (!yearDropdown.querySelector(`option[value="${year}"]`)) {
                        const option = document.createElement('option');
                        option.value = year;
                        option.textContent = year;
                        yearDropdown.appendChild(option);
                    }
                });
            } else {
                console.error('Unexpected data format:', data);
            }
        })
        .catch(error => console.error('Error fetching 10-K filings:', error));
}


function display10KLink(year) {
    const filingInfo = filingsByYear[year];
    if (filingInfo && filingInfo.type === '10-K') {
        const linkElement = document.createElement('a');
        linkElement.href = filingInfo.finalLink;
        linkElement.textContent = 'View 10-K Filing';
        linkElement.target = '_blank'; // Open in new tab

        const linkContainer = document.getElementById('link-container'); // Assuming you have a container for the link
        linkContainer.innerHTML = ''; // Clear previous link
        linkContainer.appendChild(linkElement);
    }
}



document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[type="text"]');
    const dropdown = document.createElement('ul'); // Create a dropdown list
    dropdown.classList.add('dropdown'); // Add a class for styling
    const companyNameDisplay = document.createElement('div'); // Create a div to display the company name
    companyNameDisplay.classList.add('company-name'); // Add a class for styling
    const yearDropdown = document.querySelector('select[name="year"]');
    yearDropdown.addEventListener('change', function() {
        const selectedYear = this.value;
        display10KLink(selectedYear);
    });

    document.querySelector('.search-section').appendChild(dropdown); // Append dropdown to the search section
    document.querySelector('.search-section').appendChild(companyNameDisplay); // Append company name display below the search section

    let timer;
    searchInput.addEventListener('input', function(e) {
        clearTimeout(timer);
        timer = setTimeout(function() {
            fetch(`/search-tickers?query=${e.target.value}`)
                .then(response => response.json())
                .then(data => {
                    dropdown.innerHTML = ''; // Clear previous results
                    data.forEach(item => {
                        const listItem = document.createElement('li');
                        listItem.textContent = `${item.symbol} ${item.name}`;
                        listItem.addEventListener('click', function() {
                            searchInput.value = item.symbol; // Update the input box with the symbol
                            companyNameDisplay.textContent = item.name; // Display the company name
                            populateYears(item.symbol); 
                            dropdown.innerHTML = ''; // Clear the dropdown
                        });
                        dropdown.appendChild(listItem);
                    });
                });
        }, 500); // Debounce time in milliseconds
    });

    // Hide dropdown when clicking elsewhere
    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target)) {
            dropdown.innerHTML = '';
        }
    });
});
