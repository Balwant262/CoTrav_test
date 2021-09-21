function billingTax(corporate_id , service_type, cotrav_billing_entity, corporate_billing_entity, ticket_price , no_of_passanger , oper_ticket_price = 0 , oper_cotrav_billing_entity = 0 , oper_billing_entity = 0 )
{

 			var corporate_id =  corporate_id;

            var service_type = service_type;

            var cotrav_billing_entity = cotrav_billing_entity;

            var corporate_billing_entity = corporate_billing_entity;

            var ticket_price = ticket_price;

            var url = url_tax ;

            //var url = 'http://localhost:8000/taxcalc'

    $.ajaxSetup({
            headers:{
                    'Authorization': auth_token,
                    'usertype': user_type
                }
        });

        $.post( url,{ corporate_id: corporate_id , service_type: service_type , cotrav_billing_entity: cotrav_billing_entity , corporate_billing_entity: corporate_billing_entity , ticket_price: ticket_price , no_of_passanger: no_of_passanger , oper_ticket_price: oper_ticket_price , oper_cotrav_billing_entity : oper_cotrav_billing_entity , oper_billing_entity : oper_billing_entity  },

      function(data)
      {
			var tax_details = data.Tax;
            //alert(JSON.stringify(tax_details))
			$('#ticket_price').val(tax_details.ticket_price);
			$('#mng_fee').val(tax_details.management_fee);
			$('#tax_mng_amt').val(tax_details.tax_amount_on_management_fee);
			$('#total_billing_amt').val(tax_details.sub_total);
			$('#cgst').val(tax_details.cgst);
			$('#sgst').val(tax_details.sgst);
			$('#igst').val(tax_details.igst);

			$('#tax_on_management_fee_percentage').val(tax_details.tax_on_management_fee_percentage);

			$('#oper_cgst').val(tax_details.oper_cgst);
			$('#oper_sgst').val(tax_details.oper_sgst);
			$('#oper_igst').val(tax_details.oper_igst);

			$('#management_fee_igst').val(tax_details.management_fee_igst);
			$('#management_fee_cgst').val(tax_details.management_fee_cgst);
			$('#management_fee_sgst').val(tax_details.management_fee_sgst);

			$('#management_fee_igst_rate').val(tax_details.management_fee_igst_rate);
			$('#management_fee_cgst_rate').val(tax_details.management_fee_cgst_rate);
			$('#management_fee_sgst_rate').val(tax_details.management_fee_sgst_rate);

			$('#gst_paid').val(tax_details.gst_paid);

			$('#cgst_amount').val(tax_details.oper_cgst_amount);
			$('#sgst_amount').val(tax_details.oper_sgst_amount);
			$('#igst_amount').val(tax_details.oper_igst_amount);

			$('#oper_total_excluding_tax').val(tax_details.oper_total_excluding_tax);
			$('#oper_other_charges').val(tax_details.oper_other_charges);
			$('#oper_total').val(tax_details.oper_total);
			$('#oper_gst_paid').val(tax_details.oper_gst_paid);
			$('#oper_tds_cut').val(tax_details.oper_tds_cut);
			$('#oper_sub_total').val(tax_details.oper_sub_total);


       });


}


$("#ticket_price").change(function(){

						var ticket_price = $('#ticket_price').val();

						var no_of_passanger = $('#no_of_seats').val();

						var corporate_id =  $('#corporate_id').val();

            			var service_type = serve_type;

            			var corporate_billing_entity = $("#booking_billing_entity").attr("gst");
                    	var cotrav_billing_entity = $('option:selected',"#cotrav_billing_entity").attr("gst");

           				//var cotrav_billing_entity = $('#cotrav_billing_entity').val();

           				//var corporate_billing_entity = '2fsderds';

           				var not_num = isNaN(ticket_price)

           				if(not_num)
           				{
           					alert("plz check amount");

           				}else{

           					billingTax(corporate_id , service_type , cotrav_billing_entity, corporate_billing_entity, ticket_price , no_of_passanger );
           				}

});







       $('#oper_ticket_price').keyup(function(event){
                if(event.which != 8 && isNaN(String.fromCharCode(event.which))){
                        event.preventDefault(); //stop character from entering input
                }else{

                		var ticket_price = $('#ticket_price').val();

                		var no_of_passanger = $('#no_of_seats').val();

                		var oper_ticket_price = this.value;

						var corporate_id =  $('#corporate_id').val();;

            			var service_type = serve_type;

            			var corporate_billing_entity = $("#booking_billing_entity").attr("gst");

                    	var cotrav_billing_entity = $('option:selected',"#cotrav_billing_entity").attr("gst");

                    	var oper_cotrav_billing_entity = $('option:selected',"#oper_cotrav_billing_entity").attr('gst');

                    	var oper_billing_entity = $('option:selected',"#operator_id").attr('gst');

                    	if (typeof oper_cotrav_billing_entity === 'undefined')
                    	{
                    		oper_cotrav_billing_entity = 0 ;
                    	}

                    	if (typeof oper_billing_entity === 'undefined')
                    	{
                    		oper_billing_entity = 0 ;
                    	}

           				billingTax(corporate_id , service_type , cotrav_billing_entity, corporate_billing_entity, ticket_price , no_of_passanger , oper_ticket_price , oper_cotrav_billing_entity , oper_billing_entity );

                }


            });



        $("#operator_id").change(function(){

	var opr_gst = $('option:selected', this).attr('gst');

	var no_of_passanger = $('#no_of_seats').val();

	 var ticket_price = $('#ticket_price').val();

	 var oper_ticket_price = parseFloat($('#oper_ticket_price').val());

	 var corporate_id =  $('#corporate_id').val();

	 var service_type = serve_type;

	 var corporate_billing_entity = $("#booking_billing_entity").attr("gst");

	 var cotrav_billing_entity = $('option:selected',"#cotrav_billing_entity").attr("gst");

	 var oper_cotrav_billing_entity = $('option:selected',"#oper_cotrav_billing_entity1").attr('gst');

	 var oper_billing_entity = opr_gst;

//	 alert(oper_cotrav_billing_entity);
//
//	 alert(oper_billing_entity);

	 if (typeof oper_cotrav_billing_entity === 'undefined')
                    	{
                    		oper_cotrav_billing_entity = 0 ;
                    	}

                    	if (typeof oper_billing_entity === 'undefined')
                    	{
                    		oper_billing_entity = 0 ;
                    	}

     billingTax(corporate_id , service_type , cotrav_billing_entity, corporate_billing_entity, ticket_price , no_of_passanger , oper_ticket_price , oper_cotrav_billing_entity , oper_billing_entity );


});



$("#cotrav_billing_entity1").change(function(){

	var no_of_passanger = $('#no_of_seats').val();

	var opr_gst = $('option:selected', this).attr('gst');

	var ticket_price = $('#ticket_price').val();

    var oper_ticket_price = parseFloat($('#oper_ticket_price').val());

	var corporate_id =  $('#corporate_id').val();;

    var service_type = serve_type;

    var corporate_billing_entity = $("#booking_billing_entity").attr("gst");

    var cotrav_billing_entity = $('option:selected',"#cotrav_billing_entity").attr("gst");

    var oper_cotrav_billing_entity = $('option:selected',"#cotrav_billing_entity1").attr('gst');

    var oper_billing_entity = $('option:selected',"#operator_id").attr('gst');

    if (typeof oper_cotrav_billing_entity === 'undefined')
                    	{
                    		oper_cotrav_billing_entity = 0 ;
                    	}

                    	if (typeof oper_billing_entity === 'undefined')
                    	{
                    		oper_billing_entity = 0 ;
                    	}

    billingTax(corporate_id , service_type , cotrav_billing_entity, corporate_billing_entity, ticket_price , no_of_passanger , oper_ticket_price , oper_cotrav_billing_entity , oper_billing_entity );


});


$('#total_room_price').change(function(event){

                var total_room_price = this.value;

                var checkin = $('#checkin').val();
                var checkout = $('#checkout').val();

                var a = moment(checkin, 'DD.MM.YYYY h:mm');
                var b = moment(checkout, 'DD.MM.YYYY h:mm');

                var c = new Date(a);

                var d = new Date(b);

                // To calculate the time difference of two dates
                var Difference_In_Time = d.getTime() - c.getTime();

                // To calculate the no. of days between two dates
                var Difference_In_Days = Difference_In_Time / (1000 * 3600 * 24);


                var days = Math.round(Difference_In_Days);
                 var adHour = c.getHours();
				var adMin = c.getMinutes();

				if(adMin > 0)
				{
					if(adHour != '11')
					{
						adHour += 1;
					}
				}
				var ddHour = d.getHours();
				var ddMin = d.getMinutes();
				if(ddMin > 0)
				ddHour += 1;
				if(adHour < 12 && ddHour <= 12)
				days += 1;
				if(adHour < 12 && ddHour > 12)
				{
					days += 2;
				}
				if(adHour >= 12 && ddHour > 12)
				days += 1;
				if(days > 1){
				$('#no_of_days').val(days);
				$('#no_of_days_send').val(days);
				}
				else{
				$('#no_of_days').val(1);
				$('#no_of_days_send').val(1);
				}

                room_price =  total_room_price / days;

                if(Difference_In_Days > 0 )
                {
                    $('#ticket_price').val(room_price);
                }else{

                    $('#ticket_price').val(total_room_price);
                }


                gst_per = 0;

                room_price = parseInt(room_price)

                if( room_price > 0 && room_price < 1000 )
                {
                    gst_per = 0;
                }
                else if( room_price > 1001 && room_price < 2500 )
                {
                    gst_per = 12;

                }else if( room_price > 2501 && room_price < 7500 )
                        {
                            gst_per = 18;
                        }
                        else{
                            gst_per = 28;
                        }

                // ###############

                    var ticket_price = room_price;
                    var management_fee = $('#mng_fee').val();
                    var tax_perscent_on_management_fee = 18;
                    var tax_perscentage = 0.18
                    var tax_amount_on_management_fee = 0;
                    var total_billing_amount = 0;
                    var cgst = 0.0;
                    var sgst = 0.0;
                    var igst = 0.0;


                		var no_of_passanger = $('#no_of_seats').val();

                		var oper_ticket_price = parseFloat($('#oper_ticket_price').val());

						var corporate_id =  $('#corporate_id').val();;

            			var service_type = serve_type;

            			var corporate_billing_entity = $("#booking_billing_entity").attr("gst");

                    	var cotrav_billing_entity = $('option:selected',"#cotrav_billing_entity").attr("gst");

                    	var oper_cotrav_billing_entity = $('option:selected',"#oper_cotrav_billing_entity").attr('gst');

                    	var oper_billing_entity = $('option:selected',"#operator_id").attr('gst');


                 billingTax(corporate_id , service_type , cotrav_billing_entity, corporate_billing_entity, ticket_price , no_of_passanger , oper_ticket_price , oper_cotrav_billing_entity , oper_billing_entity );




                });



  $("#hotel_name").change(function(){


var opr_gst = $('option:selected', this).attr('gst');
//alert(opr_gst);

var cgst = 0.0;
var sgst = 0.0;
var igst = 0.0;

 val1 = opr_gst;

 val2 = $('option:selected',"#oper_cotrav_billing_entity").attr("gst");

                        var ticket_price = $('#ticket_price').val();

                		var no_of_passanger = $('#no_of_seats').val();

                		var oper_ticket_price = this.value;

						var corporate_id =  $('#corporate_id').val();;

            			var service_type = serve_type;

            			var corporate_billing_entity = $("#booking_billing_entity").attr("gst");

                    	var cotrav_billing_entity = $('option:selected',"#cotrav_billing_entity").attr("gst");

                    	var oper_cotrav_billing_entity = $('option:selected',"#oper_cotrav_billing_entity").attr('gst');

                    	var oper_billing_entity = opr_gst;

                    	if (typeof oper_cotrav_billing_entity === 'undefined')
                    	{
                    		oper_cotrav_billing_entity = 0 ;
                    	}

                    	if (typeof oper_billing_entity === 'undefined')
                    	{
                    		oper_billing_entity = 0 ;
                    	}


    billingTax(corporate_id , service_type , cotrav_billing_entity, corporate_billing_entity, ticket_price , no_of_passanger , oper_ticket_price , oper_cotrav_billing_entity , oper_billing_entity );


});


        $( document ).ready(function() {

       		var corporate_id =  $('#corporate_id').val();

       		var no_of_passanger = $('#no_of_seats').val();

            var service_type = serve_type;

           	var corporate_billing_entity = $("#booking_billing_entity").attr("gst");

            var cotrav_billing_entity = $('option:selected',"#cotrav_billing_entity").attr("gst");

            var ticket_price = 0;

			billingTax(corporate_id , service_type , cotrav_billing_entity, corporate_billing_entity, ticket_price , no_of_passanger );

        });
