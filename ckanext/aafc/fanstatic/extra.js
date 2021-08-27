/***
place holder for future use
*/

// Reset Function to Clear Search Box
function resetFunction() {
        document.getElementById("field-giant-search").value = "";
        document.getElementById("search-btn").click();
}


function generate_email() {
	var link = document.getElementById('suggest_dataset_email');
        // Check language (en/fr), and generate the appropriate email.
        var lang = document.documentElement.lang;
	    if (lang == "fr"){
		link.href = "mailto:aafc.opengovernment-gouvernmentouvert.aac@canada.ca?subject=Proposez un jeu de données - Catalogue de données d'AAC&body=";
		link.href += get_french_email_body();
	    } else {
		link.href = "mailto:aafc.opengovernment-gouvernmentouvert.aac@canada.ca?subject=Suggest a Dataset - AAFC Data Catalogue&body=";
	        link.href += get_english_email_body();
	    }
}

function get_english_email_body() {
    var body = "Suggest a Dataset - AAFC Data Catalogue" + "%0D%0A"+ "%0D%0A" +
               "Please provide sufficient information regarding the dataset suggestion to ensure the request can be forwarded to the appropriate group within AAFC.";
    return body;
}

function get_french_email_body() {
    var body = "Proposez un jeu de données - Catalogue de données d'AAC." + "%0D%0A" + "%0D%0A" +
               "Veuillez fournir suffisamment de reseignements sur la suggestion du jeu de données pour vous assurer que la demande peut être transmise au groupe approprié au sein d'AAC.";
    return body;
}
