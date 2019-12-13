function bookRoom(roomid, date)
{
    name = null
    if (date == '')
    {
        alert('Please select a date.')
        return;
    }
    if (!confirm('Are you sure you want to book room ' + roomid + ' for ' + date + '?'))
        return;
    if (authcheck()['privilege'] == 'agent')
        name = $('#client_name_input').val()
    else 
        name = authcheck()['username']

    $.ajax(
        {
            url: '/bookroom',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'roomid': ''+roomid, 'date':date, 'customer_name': name}),
            type: 'POST'
        }).done(function(res)
        {
            alert(res['code'] + " " + res['bookingID'])
        })
}

function getRoom(selectedRoom)
{
    cRJ = null;
    if (selectedRoom == null)
    {
        alert("Error: No room selected.")
        return;
    }
    var a = $.ajax(
    {
        url: '/getroom',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'roomid':selectedRoom}),
        type: 'POST',
        async: false
    }).done(function (res){console.log(res)
        cRJ = JSON.parse(res)
    })

    return cRJ
}

function roomPopUp(id)
{
    var cRJ = getRoom(id)
    console.log(id)
    $('body').append(
        $('<div class="popup"></div>').append(
            $('<div class="box" style="top : -100%"></div>')
            .append(
                $('<b>Floor Number</b> <input type="text"  id = "floornumber_input"></input>')
            )
            .append(
                $('<b>Room Number</b> <input type="text"  id = "roomnumber_input"></input>')
            )
            .append(
                $('<input type="text" placeholder="Description"  id = "desc_input"></input>')
            ).append(
                $('<input type="text" placeholder="Price"  id = "price_input"></input>')
            ).append(
                $('<input type="checkbox"  id = "vaccant_input">Is Vaccant<br>')
            ).append(
                $('<input type="checkbox"  id = "ready_input">Is Ready<br>')
            ).append(
                $(`<select  id="bedtype_input"> 
                            <option value="single">Single</option>
                            <option value="twin">Twin</option>
                            <option value="double">Double</option>
                            <option value="queen">Queen</option>
                            <option value="king">King</option>
                        </select> Bed Type <br>`)
            ).append(
                $(`<select  id="bedamount_input"> 
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                </select> Bed Amount <br>`)
            ).append(
                $(` <input type="checkbox"  id="microwave_input" name="Microwave"> Microwave <br>
                <input type="checkbox"  id="balcony_input" name="Balcony"> Balcony <br> 
                <input type="checkbox"  id="ethernet_input" name="Ethernet"> Ethernet <br>
                <input type="checkbox"  id="TV_input" name="TV"> TV <br>`)
            ).append(
                $('<button style="margin-right: 10px">Close</button>').attr('onclick', '$(".popup").remove()')
            ).append(
                $('<input type="date" style="margin-right: 10px" id="booking-date-input">')
            ).append(
                $('<button style="margin-right: 10px">Book</button>').attr('onclick', 'bookRoom("'+id+'", $("#booking-date-input").val())')
            ).animate({top: '0px'}, "fast")
        )

        
    )

    if (authcheck()['privilege'] == 'agent')
    {
        $('.box').append(
            $('<select id="client_name_input">Client Name</select>')
        )

        $.ajax(
        {
            url: '/getclients',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token')}),
            type: 'POST'
        }).done(function(res)
        {
            if (res['code'] == 'failed')
            {
                alert('Failed, ' + res['message'])
                return;
            }

            res['clients'].forEach(client => {
                $('#client_name_input').append(
                    $('<option value="'+client['client_name']+'">'+client['client_name']+'</option>')
                )
            })
        })
    }

    $('#floornumber_input').val(cRJ['floornumber']).prop('readonly', true)
    $('#roomnumber_input').val(cRJ['roomnumber']).prop('readonly', true)
    $('#desc_input').val(cRJ['description']).prop('readonly', true)
    $('#price_input').val(cRJ['price']).prop('readonly', true)
    $('#vaccant_input').prop('checked', cRJ['isVaccant']=='true').prop('disabled', true)
    $('#ready_input').prop('checked', cRJ['isReady']=='true').prop('disabled', true)
    $('#microwave_input').prop('checked', cRJ['microwave']=='true').prop('disabled', true)
    $('#ethernet_input').prop('checked', cRJ['ethernet']=='true').prop('disabled', true)
    $('#balcony_input').prop('checked', cRJ['balcony']=='true').prop('disabled', true)
    $('#TV_input').prop('checked', cRJ['TV']=='true').prop('disabled', true)
    $('#bedtype_input').val(cRJ['bed']).prop('readonly', true)
    $('#bedamount_input').val(cRJ['bedamount']).prop('readonly', true)
}

function getRooms(all = false)
{
    $("#listing-box").html("")  

    json_msg = JSON.stringify(
        {
            'date': document.getElementById('date-input').value, 
            'microwave': document.getElementById('microwave').checked,
            'balcony': document.getElementById('balcony').checked,
            'ethernet': document.getElementById('ethernet').checked,
            'TV': document.getElementById('TV').checked,
            'bed-type': document.getElementById('bed-type').options[document.getElementById('bed-type').selectedIndex].value,
            'bed-amount': document.getElementById('bed-amount').options[document.getElementById('bed-amount').selectedIndex].value,
            'all':all
        }
    )

    $.ajax(
        {
            url: '/getrooms',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: json_msg,
            type: 'POST'
        }
        ).done(function(res)
        {
            res = JSON.parse(res)

            res.forEach(room =>{
                roomid=''
                if (room['floornumber'].length==1)
                    roomid+='0'+room['floornumber'];
                else
                    roomid+=room['floornumber']
                if (room['roomnumber'].length==1)
                    roomid+='00'+room['roomnumber'];
                else if (room['roomnumber'].length==2)
                    roomid+='0'+room['roomnumber'];
                else
                    roomid+=room['roomnumber'];

                $("#listing-box").append(
                    $("<div class='item'></div>")
                    .append(
                        $("<h1 style = 'margin: 0px;'>"+room['description']+"</h1><p style='margin:0'>Floor "+room['floornumber']+", Room "+room['roomnumber']+"</p>")
                    ).append(
                        $("<p style='margin:0'>Price per night: "+room['price']+"</p>")
                    ).attr('id', roomid)
                    .click(function(){roomPopUp($(this).attr('id'));})
                )
            })
        })
}