//search-pets

let petSearchButton = document.querySelectorAll('#searchForm #searchButton')[0];
let petSearchForm = document.querySelectorAll('#searchForm input');

function fetchSearchResults(event){
//     event.preventDefault();
//     let formValues = {};

//     for (let formElement of petSearchForm){
//         console.log(`${formElement.name}: ${formElement.value}`);
//     }

}

petSearchButton.addEventListener('click', fetchSearchResults);