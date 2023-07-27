fetch('../news.json')
  .then(response => response.json())
  .then(newsData => {
    // Get reference to main content container
    const contentContainer = document.getElementById('content'); 
    // Get reference to timestamp container and set its text
    const timestampDiv = document.getElementById('timestamp-div');
    timestampDiv.textContent = 'News Updated At: ' + newsData.timestamp;

    // Add super summary 
    const superSummaryContainer = document.getElementById('super-summary-container');
    const superSummary = document.getElementById('super-summary');
    superSummary.textContent = newsData.super_summary;



    
    // Get navbar
    const navbar = document.getElementById('dynamic-navbar');

    // Loop through each category
    newsData.categories.forEach((category, index) => {
      // Create category div
      const categoryDiv = document.createElement('div');
      categoryDiv.classList.add('card', 'my-4');
      categoryDiv.id = category.name.replace(/\s+/g, '-').toLowerCase(); // This line sets the id of the category div
      // Create navbar item
      const navItem = document.createElement('li');
      navItem.classList.add('nav-item');

      // Create navbar link
      const navLink = document.createElement('a');
      navLink.classList.add('nav-link');
      navLink.href = `#${categoryDiv.id}`;
      navLink.textContent = category.name;

      // Append link to item and item to navbar
      navItem.appendChild(navLink);
      navbar.appendChild(navItem);
      
      const categoryHeader = document.createElement('div');
      categoryHeader.classList.add('card-header');
      
      const categoryTitle = document.createElement('h2');
      categoryTitle.textContent = category.name;
      
      categoryHeader.appendChild(categoryTitle);
      categoryDiv.appendChild(categoryHeader);
      
      // Create card body for articles
      const cardBody = document.createElement('div');
      cardBody.classList.add('card-body');
      categoryDiv.appendChild(cardBody);
      
      // Make category sections collapsible
      categoryHeader.addEventListener('click', () => {
        if (cardBody.style.display === 'block' || cardBody.style.display === '') {
          cardBody.style.display = 'none';
        } else {
          cardBody.style.display = 'block';
        }
      });
      
      // Initially hide the card body
      // cardBody.style.display = 'none';

      // Loop through articles
      category.summaries.forEach((article, i) => {

        // Create article div
        const articleDiv = document.createElement('div');
        articleDiv.classList.add('article');

        // Add headline
        const headline = document.createElement('h5');
        headline.innerHTML = `<a href="${article.link}" target="_blank">${article.headline}</a>`;
        headline.id = `headline-${i}`;

        // Add source
        const source = document.createElement('div');
        source.classList.add('source');
        source.textContent = article.source;

        // Add summary 
        const summaryDiv = document.createElement('div');
        summaryDiv.classList.add('text');
        summaryDiv.id = `summary-${i}`;

        const excerptSpan = document.createElement('span');
        excerptSpan.textContent = article.summary.slice(0, 100) + '...';
        excerptSpan.id = `excerpt-${i}`;

        const fullSpan = document.createElement('span');
        fullSpan.textContent = article.summary;
        fullSpan.style.display = 'none';
        fullSpan.id = `full-${i}`;

        // Add "More" button
        const moreButton = document.createElement('span');
        moreButton.textContent = 'More';
        moreButton.classList.add('more-button-summary');
        moreButton.onclick = () => {
          if (fullSpan.style.display === 'none') {
            fullSpan.style.display = 'block';
            excerptSpan.style.display = 'none';
          } else {
            fullSpan.style.display = 'none';
            excerptSpan.style.display = 'inline';
          }
        };

        // Add "Share" button
        const shareButton = document.createElement('button');
        shareButton.classList.add('share-button');
        shareButton.onclick = () => {
          const textToShare = `${article.headline}\n\n${article.summary}\n\nRead more at: ${article.link}`;
          if (navigator.share) {
            navigator.share({
              title: "Shared Article from NewsPlanetAi",
              text: textToShare
            })
            .then(() => console.log('Successful share'))
            .catch((error) => console.log('Error sharing:', error.name, error.message));
          } else {
            console.log(`Share not supported on this browser, do it manually:\n${textToShare}`);
          }
        };

        // Add share icon to "Share" button
        const shareIcon = document.createElement('i');
        shareIcon.classList.add('fas', 'fa-share-alt');
        shareButton.appendChild(shareIcon);

        // Append elements
        summaryDiv.appendChild(excerptSpan);
        summaryDiv.appendChild(fullSpan);
        summaryDiv.appendChild(moreButton);
        summaryDiv.appendChild(shareButton);
        articleDiv.appendChild(headline);
        articleDiv.appendChild(source);
        articleDiv.appendChild(summaryDiv);

        // Add timestamp
        const timestampDiv = document.createElement('div');
        timestampDiv.classList.add('timestamp');
        timestampDiv.textContent = article.timestamp;
        timestampDiv.id = `timestamp-${i}`;
        articleDiv.appendChild(timestampDiv);

        cardBody.appendChild(articleDiv);
      });

      contentContainer.appendChild(categoryDiv);
    });
});
document.getElementById('search-input').addEventListener('input', function() {
  if (!this.value) {
      document.getElementById('search-results').innerHTML = '';
  } else {
      performSearch();
  }
});


function performSearch() {
    // Get the user's search query
    var query = document.getElementById('search-input').value.toLowerCase();

    // Request the JSON data from the server
    fetch('../news.json')  // Assuming 'news.json' is the path to your JSON file on the server
        .then(response => response.json())  // Parse the response as JSON
        .then(newsData => {
            // Now you can use newsData just like you used it before
            var searchResults = [];

            for (var i = 0; i < newsData.categories.length; i++) {
                var category = newsData.categories[i];

                for (var j = 0; j < category.summaries.length; j++) {
                    var summary = category.summaries[j];

                    if (summary.headline.toLowerCase().includes(query) || summary.summary.toLowerCase().includes(query)) {
                        searchResults.push(summary);
                    }
                }
            }

            displaySearchResults(searchResults);
        })
        .catch(error => console.error('Error:', error));
}
function displaySearchResults(searchResults) {
  // Get the div where the search results will be displayed
  var resultsDiv = document.getElementById('search-results');

  // Clear any previous search results
  resultsDiv.innerHTML = '';

  // Iterate over the search results
  for (var i = 0; i < searchResults.length; i++) {
      var result = searchResults[i];

      // Create a new div for this search result
      var resultDiv = document.createElement('div');
      resultDiv.className = 'result-div';  // Add a class for styling

      // Create and add the headline and summary to the result div
      var headlineElement = document.createElement('a');
      headlineElement.textContent = result.headline;
      headlineElement.href = result.link;
      headlineElement.target = '_blank';
      resultDiv.appendChild(headlineElement);

      var summaryElement = document.createElement('p');
      summaryElement.textContent = result.summary;
      resultDiv.appendChild(summaryElement);

      // Add the result div to the results div
      resultsDiv.appendChild(resultDiv);
  }
}



