function replaceTextWithWhitespace(elements) {
    elements.forEach(function(element) {
        var originalText = element.textContent;
        var spaces = '\u00A0'.repeat(originalText.length)
        element.textContent = spaces;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var wordBoxElements = document.querySelectorAll('.word-box');

    replaceTextWithWhitespace(wordBoxElements);

    wordBoxElements.forEach(function(box) {
        box.dataset.originalLength = box.textContent.length - 2;
    });

    var wordBoxElementsTitle = document.querySelectorAll('.title-box');
    wordBoxElementsTitle.forEach(function(box) {
        box.dataset.originalLength = box.dataset.originalLength -1 +2;
    });
});

document.addEventListener('mouseover', function(event) {
    if (event.target.classList.contains('word-box')) {
        var originalWidth = event.target.offsetWidth;
        event.target.style.width = originalWidth + 'px';

        var originalContent = event.target.textContent;
        event.target.dataset.originalContent = originalContent;
        // add event.target.dataset.originalLength if not already present
        var lengthNode = document.createTextNode(event.target.dataset.originalLength);
        event.target.innerHTML = '';
        event.target.appendChild(lengthNode);
    }
});

document.addEventListener('mouseout', function(event) {
    if (event.target.classList.contains('word-box')) {
        var wordNode = document.createTextNode(event.target.dataset.originalContent);
        event.target.innerHTML = '';
        event.target.appendChild(wordNode);
    }
});

var usedWords = new Set();
var previousInputs = [];
var currentInputIndex = -1;
var inputField = document.getElementById("wordInput");

inputField.addEventListener("keydown", function(event) {
    if (event.key === "ArrowUp") {
        event.preventDefault();
        currentInputIndex = Math.min(currentInputIndex + 1, previousInputs.length - 1);
        if (currentInputIndex >= 0) {
          inputField.value = previousInputs[currentInputIndex];
        }
    }
    if (event.key === "ArrowDown") {
        event.preventDefault();
        currentInputIndex = Math.max(currentInputIndex - 1, -1);
        if (currentInputIndex >= 0) {
          inputField.value = previousInputs[currentInputIndex];
        } else {
          inputField.value = ""; // Clear input if at the end of history
        }
    }
});

document.getElementById("wordForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent the default form submission
    var inputWord = document.getElementById("wordInput").value.trim().split(' ')[0].toLowerCase();
    inputWord = inputWord.replace(/[^a-zA-Z0-9]/g, '');

    currentInputIndex = -1;
    previousInputs.unshift(inputWord);

    if (inputWord.length === 0) {
        return;
    }

    if ((/[a-zA-Z]/.test(inputWord)) && (/\d/.test(inputWord))) {
        document.getElementById("input-info").innerHTML = "Input '" + inputWord + "' is not a valid word.";

        document.getElementById("wordInput").value = '';
        return;
    }

    if (usedWords.has(inputWord)) {
        document.getElementById("input-info").innerHTML = "Input '" + inputWord + "' has already been used.";

        document.getElementById("wordInput").value = '';
        return;
    }

    usedWords.add(inputWord);
    addRow(inputWord);

    
    // clear the input field
    document.getElementById("wordInput").value = '';
    var addWordUrl = this.getAttribute('data-add-word-url');
    fetch(addWordUrl, {  // Use url_for to get the correct URL
        method: 'POST',
        body: new URLSearchParams({word: inputWord}),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'added') {
            console.log(data);
            result = data.result; // json {index, word}

            var previously_guessed = document.getElementsByClassName('word-box-guessed');
            var guessedArray = Array.from(previously_guessed); // Convert live HTMLCollection to static array
            for (var i = 0; i < guessedArray.length; i++) {
                guessedArray[i].classList.remove('word-box-guessed');
                guessedArray[i].classList.remove('word-box-similarity');
                guessedArray[i].textContent = guessedArray[i].textContent.trim()
            }
            
            var boxes = document.getElementsByClassName("word");
            for (const index in result) {
                if (typeof result[index] === 'string') {
                    boxes[index].classList.remove('word-box-similarity');
                    boxes[index].classList.remove('word-box');
                    boxes[index].classList.add('word-box-guessed');
                    boxes[index].textContent = "\u00A0" + result[index] + "\u00A0";

                    // get the number from span element with id='num_guessed' and increment it
                    var num_guessed = document.getElementById('num_guessed');
                    var num_guessed_value = parseInt(num_guessed.textContent);
                    num_guessed.textContent = num_guessed_value + 1;

                    
                }
                if (typeof result[index] === 'number') {
                    boxes[index].classList.add('word-box-similarity');
                    boxes[index].textContent = "\u00A0" + inputWord + "\u00A0";
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

function addRow(word) {
    var table = document.getElementById("game-stats-words-entered");
    var rowCount = table.rows.length;

    var row = table.insertRow(1);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);

    cell1.innerHTML = rowCount;
    cell2.innerHTML = word;
}