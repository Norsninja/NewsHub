document.addEventListener('DOMContentLoaded', function() {
    let currentArticle = 0;
    const categoryColors = {
        "world-news": { color1: "#1E90FF", color2: "#104E8B" },
        "us-news": { color1: "#FF4500", color2: "#8B2500" },
        "economy-finance": { color1: "#32CD32", color2: "#228B22" },
        "health-environment": { color1: "#8A2BE2", color2: "#551A8B" },
        "science-research": { color1: "#FFD700", color2: "#8B7500" },
        "space": { color1: "#87CEEB", color2: "#4A708B" },
        "technology-innovation": { color1: "#FF69B4", color2: "#8B3A62" },
        "society-culture": { color1: "#CD853F", color2: "#8B4513" },
        "sports": { color1: "#7CFC00", color2: "#437200" },
        "law-crime": { color1: "#DC143C", color2: "#8B0A50" },
        "russia-ukraine-conflict": { color1: "#000080", color2: "#000040" },
        "default": { color1: "#39464D", color2: "#1B1B1B" }
      };
      

      function createArticleDiv(article, i, category) {
        let articleDiv = document.createElement('div');
        articleDiv.id = 'article-' + i; // Assign the ID here
        let className = category.replace(/\s&\s/g, '-').replace(/\s/g, '-').toLowerCase();
        articleDiv.className = 'article-card ' + className + (i !== 0 ? ' hidden' : '');
    
        // Get the gradient colors based on the category
        let colors = categoryColors[className];
    
        let svgElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svgElement.setAttributeNS(null, "viewBox", "0 0 100 100");
        svgElement.style.width = '100%';
        svgElement.style.maxWidth = '600px';
        svgElement.style.height = '100%';
        svgElement.style.position = 'relative';
        svgElement.style.top = '0';
        svgElement.style.left = '0';
    
        let gradientID = 'gradient-' + i; // Unique gradient ID
        let linearGradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
        linearGradient.setAttributeNS(null, "id", gradientID); // Set unique ID here
        linearGradient.setAttributeNS(null, "gradientTransform", "rotate(45)");
    
        let stop1 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        stop1.setAttributeNS(null, "offset", "0%");
        stop1.setAttributeNS(null, "stop-color", colors.color1);
    
        let stop2 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        stop2.setAttributeNS(null, "offset", "100%");
        stop2.setAttributeNS(null, "stop-color", colors.color2);
    
        linearGradient.appendChild(stop1);
        linearGradient.appendChild(stop2);
        svgElement.appendChild(linearGradient);
    
        let polygon = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
        polygon.setAttributeNS(null, "points", "0,0 100,0 100,100");
        polygon.setAttributeNS(null, "fill", "url(#" + gradientID + ")"); // Use the unique gradient ID
        svgElement.appendChild(polygon);
    
        articleDiv.appendChild(svgElement);
        articleDiv.style.position = 'relative';
        // Create a container for the text content
        let contentDiv = document.createElement('div');
        contentDiv.style.position = 'absolute'; // Position absolute to cover the entire articleDiv
        contentDiv.style.width = '100%'; // Full width of the parent
        contentDiv.style.height = '100%'; // Full height of the parent
        contentDiv.style.top = '0'; // Align to the top of the parent
        contentDiv.style.left = '0'; // Align to the left of the parent
        contentDiv.style.zIndex = '1'; // Set the z-index above the SVG

        // Flex properties to center content
        contentDiv.style.display = 'flex';
        contentDiv.style.flexDirection = 'column';
        contentDiv.style.justifyContent = 'center';
        contentDiv.style.alignItems = 'center';
        contentDiv.style.textAlign = 'center';
    

        let headline = document.createElement('h2');
        // Create a temporary div to decode HTML entities
        let tempDiv = document.createElement('div');
        tempDiv.innerHTML = article.headline;

        // Assign the decoded headline to the h2 element
        headline.textContent = tempDiv.textContent;
        contentDiv.appendChild(headline);

        let categoryElement = document.createElement('p');
        categoryElement.textContent = 'Category: ' + category;
        contentDiv.appendChild(categoryElement);
        
        
        let timestampElement = document.createElement('p');
        timestampElement.textContent = 'Published: ' + article.timestamp;
        contentDiv.appendChild(timestampElement);

        let summary = document.createElement('p');
        summary.textContent = article.summary;
        summary.className = 'hidden';  // Hide the summary initially
        contentDiv.appendChild(summary);

        let link = document.createElement('a');
        link.href = article.link;
        link.textContent = 'Read more';
        link.target = '_blank';
        link.className = 'hidden';  // Hide the link initially
        contentDiv.appendChild(link);
         // Append the SVG and contentDiv to the articleDiv
        articleDiv.appendChild(svgElement);
        articleDiv.appendChild(contentDiv); // Append contentDiv to articleDiv

        headline.addEventListener('click', function() {
            summary.classList.toggle('hidden');
            link.classList.toggle('hidden');
        });

        document.getElementById('articles').appendChild(articleDiv);
    }

    let newsData = null;

    function getNumArticles() {
        if (newsData) {
        return newsData.categories.flatMap(category => category.summaries).length;
        }
        return 0;
    }

    function displayNewsData(newsData) {
        let articleIndex = 0;
        newsData.categories.forEach(category => {
            category.summaries.forEach((summary, i) => {
                createArticleDiv(summary, articleIndex++, category.name);
            });
        });
    }

fetch('../news.json')
        .then(response => response.json())
        .then(data => {
            newsData = data;
            displayNewsData(data);
        })
        .catch(error => console.error('Error:', error));

    function showNextArticle() {
        document.getElementById('article-' + currentArticle).classList.add('hidden');
        currentArticle = (currentArticle + 1) % getNumArticles();
        let nextArticleElement = document.getElementById('article-' + currentArticle);

        if (nextArticleElement) {
            nextArticleElement.classList.remove('hidden');
        } else {
            let message = document.createElement('p');
            message.textContent = 'No more articles in this category. Please select a new category.';
            document.getElementById('articles').appendChild(message);
        }
    }


    document.getElementById('next-button').addEventListener('click', showNextArticle);

function showPreviousArticle() {
  document.getElementById('article-' + currentArticle).classList.add('hidden');
  currentArticle = (currentArticle - 1 + getNumArticles()) % getNumArticles();
  document.getElementById('article-' + currentArticle).classList.remove('hidden');
}


let startX = 0; // Starting X coordinate
let startY = 0; // Starting Y coordinate

// Function to handle the start of a touch event
function touchStart(event) {
  startX = event.touches[0].clientX;
  startY = event.touches[0].clientY;
}

// Function to handle the end of a touch event
function touchEnd(event) {
  let endX = event.changedTouches[0].clientX;
  let endY = event.changedTouches[0].clientY;
  
  // Calculate the swipe direction
  let diffX = endX - startX;
  let diffY = endY - startY;

  // Detecting left and right swipes (ignoring vertical swipes)
  if (Math.abs(diffX) > Math.abs(diffY)) {
    if (diffX > 0) {
      showPreviousArticle(); // Swipe right
    } else {
      showNextArticle(); // Swipe left
    }
  }
}

// Adding event listeners
let articlesContainer = document.getElementById('articles');
articlesContainer.addEventListener('touchstart', touchStart);
articlesContainer.addEventListener('touchend', touchEnd);

    document.getElementById('category-select').addEventListener('change', function() {
        let selectedCategory = this.value;
    
        // Clear previous articles
        document.getElementById('articles').innerHTML = '';
    
        // Reset currentArticle
        currentArticle = 0;
    
        // Filter and display news data
        let articleIndex = 0;
        newsData.categories.forEach(category => {
            if (selectedCategory === '' || category.name === selectedCategory) {
                category.summaries.forEach((summary, i) => {
                    createArticleDiv(summary, articleIndex++, category.name);
                });
            }
        });
    });
});