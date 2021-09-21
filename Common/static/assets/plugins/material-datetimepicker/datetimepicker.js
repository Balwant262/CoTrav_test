$(document).ready(function()
		{
			$('#date').bootstrapMaterialDatePicker
			({
				time: false,
				clearButton: true
			});
			$('#date1').bootstrapMaterialDatePicker
			({
				time: false,
				clearButton: true
			});
			$('#date2').bootstrapMaterialDatePicker
			({
				time: false,
				clearButton: true
			});
			$('#dateOfBirth').bootstrapMaterialDatePicker
			({
				time: false,
				clearButton: true
			});

			$('#therapyDate').bootstrapMaterialDatePicker
			({
				time: false,
				clearButton: true
			});
			
			$('#time').bootstrapMaterialDatePicker
			({
				date: false,
				shortTime: false,
				format: 'HH:mm'
			});
			$('#time2').bootstrapMaterialDatePicker
			({
				date: false,
				shortTime: false,
				format: 'HH:mm'
			});

			$('.date-format').bootstrapMaterialDatePicker
			({
				format: 'DD-MM-YYYY HH:mm:ss'
			});
			$('.date').bootstrapMaterialDatePicker
			({
			    time: false,
				format: 'DD-MM-YYYY',
			}).on('change', function(e, date)
			{
				$('.date').bootstrapMaterialDatePicker('setMinDate', date);
			});
			$('.time').bootstrapMaterialDatePicker
			({
			    date: false,
				format: 'HH:mm'
			}).on('change', function(e, date)
			{
				$('.time').bootstrapMaterialDatePicker('setMinDate', date);
			});;

			$('#date-fr').bootstrapMaterialDatePicker
			({
				format: 'DD/MM/YYYY HH:mm',
				lang: 'fr',
				weekStart: 1, 
				cancelText : 'ANNULER',
				nowButton : true,
				switchOnClick : true
			});

			$('#date-end').bootstrapMaterialDatePicker
			({
				weekStart: 0, format: 'DD/MM/YYYY HH:mm'
			});
			$('#date-start').bootstrapMaterialDatePicker
			({
				weekStart: 0, format: 'DD/MM/YYYY HH:mm', shortTime : true
			}).on('change', function(e, date)
			{
				$('#date-end').bootstrapMaterialDatePicker('setMinDate', date);
			});

			$('#min-date').bootstrapMaterialDatePicker({ format : 'DD/MM/YYYY HH:mm:ss', minDate : new Date() });

			
		});