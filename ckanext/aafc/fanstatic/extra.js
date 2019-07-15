/***
temp home for experimental code
*/

function changeLang( lang ){
   if (lang == "en"){
      $("#langFr").addClass("hidden");
      $("#langEn").removeClass("hidden");
      console.log("now in fr branch");
   }
   else{
      $("#langEn").addClass("hidden");
      $("#langFr").removeClass("hidden");
   }
   console.log("switched to language: " +  lang);
}

/*
function conditionalShow(){
	var selected = $(this).val();
	if(selected == "internal")
          //$("#group-Open-Government-Dataset-Release-Information").addClass("hidden");
	  switchToInternal();
	else
          //$("#group-Open-Government-Dataset-Release-Information").removeClass("hidden");
	  switchToOpenGovernment();

}
*/
$('#langEn').click(function(){changeLang("fr");});
$('#langFr').click(function(){changeLang("en");});
