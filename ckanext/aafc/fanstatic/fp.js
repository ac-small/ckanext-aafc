/***
Javascript to populate front page (landing page)
with statistics on last modified, and most popular
datasets.
API calls use last_modified field and total_views.
For consistency, only public records will be returned.
*/

var lang = document.documentElement.lang;

(function($) {
	$(document).ready(function() {
		var recentDatasetsURL = "api/action/package_search?q=&sort=metadata_modified+desc&rows=5";
		var popularDatasetsURL = "api/action/package_search?q=&sort=total_views+desc&rows=5";

		var recent_data = {}
		var popular_data = {}

		setTimeout(function() {
			$.ajax({
				type: 'GET',
				url: recentDatasetsURL,
				error: function(req, err){ console.log('Ajax error querying for recently modified datasets : ' + err);}
			})
			.done(function(result) {
				recent_data.recent_datasets = result.result.results;
				updateCKANData(recent_data);

			});
		}, 10);


                setTimeout(function() {
                        $.ajax({
                                type: 'GET',
                                url: popularDatasetsURL,
                                error: function(req, err){ console.log('Ajax error querying for most popular datasets : ' + err);}
                        })
                        .done(function(result) {
                                popular_data.popular_datasets = result.result.results;
                                updateCKANData(popular_data);

                        });
                }, 10);


	});

	function updateCKANData(feedData) {

		if(feedData.recent_datasets) {
			populateCKANContainer(feedData.recent_datasets, '.recent-datasets');
		}

		if(feedData.popular_datasets) {
			populateCKANContainer(feedData.popular_datasets, '.popular-datasets');
		}
	}

	function populateCKANContainer(datasets, eleTarget) {
		var $container = $(eleTarget);

		if($container.length > 0) {
			$container.empty();

			for(var i in datasets) {
				var dataset = datasets[i];
				console.log(dataset);
				if (lang == "fr"){
				    $container.append($('<li></li>').html($('<a></a>').attr('href', "dataset/" + dataset.id).html(dataset.title_translated.fr)));
				} else {
				    $container.append($('<li></li>').html($('<a></a>').attr('href', "dataset/" + dataset.id).html(dataset.title_translated.en)));
				}
			}
		}
	}
})(jQuery);
