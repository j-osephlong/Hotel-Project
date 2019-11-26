var selectedClient = null

function showBookings()
{
    $.ajax(
        {
            url: '/getbookings',
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

            $('#control-box').html('');

            res['bookings'].forEach(booking => {
                $('#control-box').append(
                    $('<div class="item"></div>')
                    .append(
                        $('<p>'+booking['bookingID']+'</p>')
                    )
                    .attr('id', booking['bookingID'])
                    .click(function(){getReciept($(this).attr('id'))})

                    //add more
                )
            });
        })
}

function changePassDialog()
{
    $('body').append(
        $('<div class="popup"></div>').append(
            $('<div class="box" style="top : -100%"></div>')
            .append(
                $('<div class="header-text">Change Password</div>')
            )
            .append(
                $('<input type="password" placeholder="Old Password"  id = "oldpass_input"></input>')
            )
            .append(
                $('<input type="password" placeholder="New Password" style="margin-bottom: 10px" id = "newpass_input"></input>')
            )
            .append(
                $('<button style="margin-right: 10px">Cancel</button>').attr('onclick', '$(".popup").remove()')
            )
            .append(
                $('<button onclick="changePass()">Change</button>')
            ).animate({top: '0px'}, "fast")
        )
    )
}

function changePass()
{
    $.ajax(
        {
            url: '/changepassword',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'oldpass' : $('#oldpass_input').val(), 'newpass': $('#newpass_input').val()}),
            type: 'POST'
        }).done(function (res)
        {
            alert(res['code'] + ', ' + res['message'])
            $(".popup").remove()
            window.location.href = '/'
        })
}

function cancelBooking(id)
{
    $.ajax(
        {
            url: '/cancelbooking',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'bookingID' : id}),
            type: 'POST'
        }).done(function (res)
        {
            alert(res['code'] + ', ' + res['message'])
        })
}

function recieptPopUp(id)
{
    reciept = id['reciept']

    $('body').append(
        $('<div class="popup"></div>').append(
            $('<div class="box" style="top : -100%"></div>')
            .append(
                $('<div class="header-text">Receipt</div>')
            )
            .append(
                $('<p>Floor number: '+reciept['floornumber']+' Room number:'+reciept['roomnumber']+'</p>')
            )
            .append(
                $('<p>Username: '+reciept['username']+', Customer Name: '+reciept['customer_name']+'</p>')
            )
            .append(
                $('<p>Date: '+reciept['date']+'</p>')
            )
            .append(
                $('<p>Total: '+reciept['price']+'</p>')
            )
            .append(
                $('<p>Booking ID: '+reciept['bookingID']+', Tranac ID: '+reciept['transID']+'</p>')
            )
            .append(
                $('<button style="margin-right: 10px">Close</button>').attr('onclick', '$(".popup").remove()')
            )
            .append(
                $('<button>Cancel Booking</button>')
                .click(function(){cancelBooking(id['reciept']['bookingID'])})
            )
            .animate({top: '0px'}, "fast")
        )
    )
}

function showClients()
{
    if (authcheck()['privilege'] != 'agent')
    {
        alert('You are not an agent.');
        return;
    }

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

            $('#control-box').html('');

            res['clients'].forEach(client => {
                $('#control-box').append(
                    $('<div class="item"></div>')
                    .append(
                        $('<p>'+client['client_name']+'</p>')
                    )
                    .append(
                        $('<p>'+client['client_email']+'</p>')
                    )
                    .attr('id', client['client_email'])
                    .append(
                        $('<button>Remove Client</button>')
                        .click(function(){removeClient(client['client_email'])})
                    )
                    

                    //add more
                )
            });
        })
}

function addClientDialog()
{
    $('body').append(
        $('<div class="popup"></div>').append(
            $('<div class="box" style="top : -100%"></div>')
            .append(
                $('<div class="header-text">Add Client</div>')
            )
            .append(
                $('<input type="text" placeholder="Client Name"  id = "name_input"></input>')
            )
            .append(
                $('<input type="text" placeholder="Client Email" style="margin-bottom: 10px" id = "email_input"></input>')
            )
            .append(
                $('<button style="margin-right: 10px">Close</button>').attr('onclick', '$(".popup").remove()')
            )
            .append(
                $('<button onclick="addClient()">Add</button>')
            ).animate({top: '0px'}, "fast")
        )
    )
}

function removeClient(client_email)
{
    if (authcheck()['privilege'] != 'agent')
    {
        alert('You are not an agent.');
        return;
    }

    $.ajax(
        {
            url: '/removeclient',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'client_email': client_email}),
            type: 'POST'
        }).done(function(res){alert(res['code'] + ", " + res['message'])})
}

function addClient()
{
    if (authcheck()['privilege'] != 'agent')
    {
        alert('You are not an agent.');
        return;
    }

    $.ajax(
        {
            url: '/addclient',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'client_name': $('#name_input').val(), 'client_email': $('#email_input').val()}),
            type: 'POST'
        }).done(function(res){alert(res['code'] + ", " + res['message'])})

    $(".popup").remove()
}

function getReciept(bookingID)
{
    $.ajax(
        {
            url: '/getreciept',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'bookingID': bookingID}),
            type: 'POST'
        }).done(function(res)
        {
            console.log(res)
            recieptPopUp(res)
        })
}