// let petSpecieSelection = document.getElementById('pet_specie');
let petSpecieSelection = document.getElementsByName('pet_specie');
let primaryBreedSelection = document.getElementById('primary_breed');

function returnPetBreeds(petSpecieID){

    fetch(`/api/breeds/${petSpecieID}`).then(function(response){

        response.json().then(function(data){
                
            breedOptionHTML = '';

            for(let breed of data.breeds) {
                    
                breedOptionHTML += `<option values="${breed.id}">${breed.breed_name}</option>`;

            }

            primaryBreedSelection.innerHTML = breedOptionHTML;

        });

    });
}

window.addEventListener('load', (event) => {

    petSpecieSelection.forEach((element) => {
        if (element.checked){
            
            selectedPetSpecieID = element.value;
        }
    });

    returnPetBreeds(selectedPetSpecieID);

});

for (selection of petSpecieSelection){
        
    selection.addEventListener("click", (event) => {
        
        selectedPetSpecieID = event.target.value;
        returnPetBreeds(selectedPetSpecieID);
        
    });

}
