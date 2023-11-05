// This function fetches new data from the server and updates the HTML page
function fetchData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            // 'data' is an array of messages from the server

            // Select the element where you want to display the data
            const displayElement = document.getElementById('display');

            // Clear any existing data in the element
            displayElement.innerHTML = '';

            // Loop over each message and add it to the display element
            for (const message of data) {
                const paragraph = document.createElement('p');
                paragraph.textContent = `Name: ${message.name}, Age: ${message.age}, Nationality: ${message.nationality}, Timestamp: ${message.timestamp}`;
                displayElement.appendChild(paragraph);
            }
        });
}

// Call fetchData every 5 seconds
setInterval(fetchData, 5000);
