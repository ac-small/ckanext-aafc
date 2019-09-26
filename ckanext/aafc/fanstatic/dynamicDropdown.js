/***
for selection of dropdown  
 Program Alignment Architecture to DRF Core Responsibilities
change the option of dropdown
 DRF Program Inventory

*/


var paa2drfData0 = 
{
 "domestic_and_international_markets":
	['Trade and Market Expansion','Sector Engagement and Development','Farm Products Council of Canada','Dairy Programs','Canadian Pari-Mutuel Agency','Water Infrastructure','Community Pastures','Federal, Provincial and Territorial Cost-shared Markets and Trade'],
 "science_and_innovation":
	['Foundational Science and Research','AgriScience','AgriInnovate','Agricultural Greenhouse Gases Program','Canadian Agricultural Adaptation Program','Federal, Provincial and Territorial Cost-shared Science, Research, Innovation and Environment'],
 "sector_risk":
	['AgriStability','AgriInsurance','AgriRisk','AgriInvest','AgriRecovery','Loan Guarantee Programs','Farm Debt Mediation Service','Pest Management','Assurance Program','Federal, Provincial and Territorial Cost-shared Assurance','Return of Payments'],
 "internal_services":
	['Management and Oversight Services','Communication Services','Legal Services','Human Resource Management Services','Financial Management Services','Information Management Services','Information Technology Services','Real Property Services','Material Services','Acquisition Services']
};

var dic = {}
$('ul.mdpd').each( 
    function(index) { 
        console.log("index:" +index);
        var chidren = this.childNodes;
        var parent = this.id;
        dic[parent] = [];
        chidren.forEach ( function (data){
           var id = data.id;
           var label = data.innerText;
           //dic[parent].push({"value":id,"lable":label});
           dic[parent].push(label);
        });
    }

 );

var paa2drfData = dic;




$("#field-program_alignment_architecture_to_drf_core_responsibilities").change(
	function(){
	    $("#field-drf_program_inventory").empty();
		var parent = $(this).children("option:selected").val();
		var children = paa2drfData[parent];
		children.forEach ( function(item) {
		    var val = item.toLowerCase().replace(/\s/g,"_");
            $("#field-drf_program_inventory").append(
                $('<option></option>').val(val).html(item)
            );
		})
	}
);


