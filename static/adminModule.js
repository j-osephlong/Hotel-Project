var selectedUser = null;
var currentRoomJSON = null;
var selectedRoom = null;

function approveUser(username)
{
    if (username === null)
        return;
    console.log('Requesting approval of ' + username)
    $.ajax(
    {
        url: '/approveuser',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'username' : username}),
        type: 'POST'
    })
    .done(function (res)
    {
        alert(res['code'])
    })

    getUsers()
}

function deleteRoom()
{
    if (selectedRoom == null)
    {
        alert("No room selected.")
        return;
    }
    
    $.ajax(
    {
        url: '/admin_deleteroom',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'roomid':selectedRoom}),
        type: 'POST'
    }).done(function (res) 
    {
        alert(res['code'] + ", " + res['message'])
    })
}

function getUsers()
{
    $('#control_box').html('<div class=\'header_text\'>Users</div>')
    $.ajax(
    {
        url: '/admin_getusers',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'token':$.cookie('jwtauth_token')}),
        type: 'POST'
    }).done(function (res)
    {
        res = JSON.parse(res)
        res = JSON.parse(res)

        $('#control_box').append
        (
            $('<table></table>').append(
                $('<thead></thead>').append(
                    $('<tr></tr>').append(
                        $('<td>Username</td>')
                    ).append(
                        $('<td>Privilege</td>')
                    ).append(
                        $('<td>Banned</td>')
                    ).append(
                        $('<td>Time of Creation</td>')
                    )
                )
            ).append(
                $('<tbody></tbody>')
            ).attr('id', 'requests_table').attr('margin-top', '15px')
        ).append(
            $('<button>Ban/Unban</button>').attr('onclick', 'banUser(selectedUser)')
        ).append(
            $('<button>Change Privilege</button>').attr('onclick', 'setUserPriv(selectedUser)')
        ) 

        res.forEach(user => {
            $('#requests_table > tbody').append(
                $('<tr></tr>').attr('id', user['username'])
                .append(
                    $('<td>'+user['username']+'</td>')
                ).append(
                    $('<td>'+user['privilege']+'</td>')
                ).append(
                    $('<td>'+user['banned']+'</td>')
                ).append(
                    $('<td>'+user['time']+'</td>')
                ).click(function (e)
                {
                    $(e.currentTarget).css('background-color', 'cornflowerblue').siblings().css('background-color', 'inherit')
                    selectedUser = $(e.currentTarget).attr('id');
                })
            )
        });   
        $('#requests_table').focus()
    })
}

function getRoomsAdmin()
{
    $('#control_box').html('<div class=\'header_text\'>Rooms</div>')
    $.ajax(
    {
        url: '/admin_getrooms',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'token':$.cookie('jwtauth_token')}),
        type: 'POST'
    }).done(function (res)
    {
        res = JSON.parse(res)
        res = JSON.parse(res)

        $('#control_box').append
        (
            $('<table></table>').append(
                $('<thead></thead>').append(
                    $('<tr></tr>').append(
                        $('<td>Floor#</td>')
                    ).append(
                        $('<td>Room#</td>')
                    ).append(
                        $('<td>Vaccant</td>')
                    ).append(
                        $('<td>Ready</td>')
                    ).append(
                        $('<td>Price</td>')
                    )
                )
            ).append(
                $('<tbody></tbody>')
            ).attr('id', 'room_table').attr('margin-top', '15px')
        ).append(
            $('<button>Add Room</button>').attr('onclick', 'createRoomDialog()')
        ) .append(
            $('<button>Edit Room</button>').attr('onclick', 'editRoomDialog()')
        )
        .append(
            $('<button>Delete Room</button>').attr('onclick', 'deleteRoom()')
        ) 

        res.forEach(room => {
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

            $('#room_table > tbody').append(
                $('<tr></tr>').attr('id', roomid)
                .append(
                    $('<td>'+room['floornumber']+'</td>')
                ).append(
                    $('<td>'+room['roomnumber']+'</td>')
                ).append(
                    $('<td>'+room['isVaccant']+'</td>')
                ).append(
                    $('<td>'+room['isReady']+'</td>')
                ).append(
                    $('<td>'+room['price']+'</td>')
                ).click(function (e)
                {
                    $(e.currentTarget).css('background-color', 'cornflowerblue').siblings().css('background-color', 'inherit')
                    currentRoomJSON = getRoom($(e.currentTarget).attr('id'));
                    selectedRoom = $(e.currentTarget).attr('id');
                })
            )
        });   
        $('#room_table').focus()
    })
}

function submitRoomEdit()
{
    if (currentRoomJSON == null)
    {
        alert("Error: No room selected.")
        return;
    }

    currentRoomJSON['description'] = $('#desc_input').val()
    currentRoomJSON['price'] = $('#price_input').val()
    currentRoomJSON['isVaccant'] = $('#vaccant_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['isReady'] = $('#ready_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['microwave'] = $('#microwave_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['ethernet'] = $('#ethernet_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['balcony'] = $('#ethernet_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['TV'] = $('#TV_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['bed'] = $('#bedtype_input').val()
    currentRoomJSON['bedamount'] = $('#bedamount_input').val()

    $.ajax(
        {
            url: '/admin_editroom',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'update': currentRoomJSON}),
            type: 'POST'
        }).done(function (res){
            alert(res['code'] + ", " + res['message'])  
        })

    $(".popup").remove()
    getRoomsAdmin()
}

function editRoomDialog()
{
    if (currentRoomJSON == null)
    {
        alert("Error: No room selected.")
        return;
    }
    $('body').append(
        $('<div class="popup"></div>').append(
            $('<div class="box" style="top : -100%"></div>')
            .append(
                $('<input type="text" placeholder="Description" id = "desc_input"></input>')
            ).append(
                $('<input type="text" placeholder="Price" id = "price_input"></input>')
            ).append(
                $('<input type="checkbox" id = "vaccant_input">Is Vaccant<br>')
            ).append(
                $('<input type="checkbox" id = "ready_input">Is Ready<br>')
            ).append(
                $(`<select id="bedtype_input"> 
                            <option value="single">Single</option>
                            <option value="twin">Twin</option>
                            <option value="double">Double</option>
                            <option value="queen">Queen</option>
                            <option value="king">King</option>
                        </select> Bed Type <br>`)
            ).append(
                $(`<select id="bedamount_input"> 
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                </select> Bed Amount <br>`)
            ).append(
                $(` <input type="checkbox" id="microwave_input" name="Microwave"> Microwave <br>
                <input type="checkbox" id="balcony_input" name="Balcony"> Balcony <br> 
                <input type="checkbox" id="ethernet_input" name="Ethernet"> Ethernet <br>
                <input type="checkbox" id="TV_input" name="TV"> TV <br>`)
            ).append(
                $('<button>Close</button>').attr('onclick', '$(".popup").remove()')
            ).append(
                $('<button>Submit</button>').attr('onclick', 'submitRoomEdit()')
            ).animate({top: '0px'}, "fast")
        )
    )

    //set them
    $('#desc_input').val(currentRoomJSON['description'])
    $('#price_input').val(currentRoomJSON['price'])
    $('#vaccant_input').prop('checked', currentRoomJSON['isVaccant']=='true')
    $('#ready_input').prop('checked', currentRoomJSON['isReady']=='true')
    $('#microwave_input').prop('checked', currentRoomJSON['microwave']=='true')
    $('#ethernet_input').prop('checked', currentRoomJSON['ethernet']=='true')
    $('#balcony_input').prop('checked', currentRoomJSON['balcony']=='true')
    $('#TV_input').prop('checked', currentRoomJSON['TV']=='true')
    $('#bedtype_input').val(currentRoomJSON['bed'])
    $('#bedamount_input').val(currentRoomJSON['bedamount'])
}

function submitRoomCreate()
{
    currentRoomJSON['floornumber'] = $('#floornumber_input').val()
    currentRoomJSON['roomnumber'] = $('#roomnumber_input').val()
    currentRoomJSON['description'] = $('#desc_input').val()
    currentRoomJSON['price'] = $('#price_input').val()
    currentRoomJSON['isVaccant'] = $('#vaccant_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['isReady'] = $('#ready_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['balcony'] = $('#balcony_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['microwave'] = $('#microwave_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['ethernet'] = $('#ethernet_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['TV'] = $('#TV_input').is(':checked') ? 'true' : 'false';
    currentRoomJSON['bed'] = $('#bedtype_input').val()
    currentRoomJSON['bedamount'] = $('#bedamount_input').val()

    $.ajax(
        {
            url: '/admin_createroom',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'update': currentRoomJSON}),
            type: 'POST'
        }).done(function (res){
            alert(res)  
        })

    $(".popup").remove()
    getRooms();
}

function createRoomDialog()
{
    currentRoomJSON = {
        'floornumber' : '', 'roomnumber':'',
        'isVaccant' : '', 'isReady' : '',
        'description' : '', 'price' : '',
        'bed' : '', 'microwave' : '',
        'balcony' : '', 'ethernet' : '',
        'TV' : '', 'bedamount' : ''
    }

    $('body').append(
        $('<div class="popup"></div>').append(
            $('<div class="box" style="top : -100%"></div>')
            .append(
                $('<b>Floor Number</b> <input type="number" id = "floornumber_input"></input>')
            )
            .append(
                $('<b>Room Number</b> <input type="number" id = "roomnumber_input"></input>')
            )
            .append(
                $('<input type="text" placeholder="Description" id = "desc_input"></input>')
            ).append(
                $('<input type="text" placeholder="Price" id = "price_input"></input>')
            ).append(
                $('<input type="checkbox" id = "vaccant_input">Is Vaccant<br>')
            ).append(
                $('<input type="checkbox" id = "ready_input">Is Ready<br>')
            ).append(
                $(`<select id="bedtype_input"> 
                            <option value="single">Single</option>
                            <option value="twin">Twin</option>
                            <option value="double">Double</option>
                            <option value="queen">Queen</option>
                            <option value="king">King</option>
                        </select> Bed Type <br>`)
            ).append(
                $(`<select id="bedamount_input"> 
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                </select> Bed Amount <br>`)
            ).append(
                $(` <input type="checkbox" id="microwave_input" name="Microwave"> Microwave <br>
                <input type="checkbox" id="balcony_input" name="Balcony"> Balcony <br> 
                <input type="checkbox" id="ethernet_input" name="Ethernet"> Ethernet <br>
                <input type="checkbox" id="TV_input" name="TV"> TV <br>`)
            ).append(
                $('<button>Close</button>').attr('onclick', '$(".popup").remove()')
            ).append(
                $('<button>Submit</button>').attr('onclick', 'submitRoomCreate()')
            ).animate({top: '0px'}, "fast")
        )
    )
}

function setUserPriv(username)
{
    var priv = prompt('Please enter privilege level.\n\'user\', \'admin\', \'agent\'', 'user')
    $.ajax(
        {
            url: '/setuserpriv',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'username':username, 'priv':priv}),
            type: 'POST'
        }).done(function (res)
        {
            alert(res['code'] + " " + res['message'])
        })

    getUsers()
}

function banUser(username)
{
    $.ajax(
        {
            url: '/banuser',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token'), 'username':username}),
            type: 'POST'
        }).done(function (res)
        {
            alert(res['code'] + " " + res['message'])
        })

    getUsers()
}

function getAccountRequests()
{
    $('#control_box').html('<div class=\'header_text\'>Account Requests</div>')
    $.ajax(
    {
        url: '/admin_accountrequests',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'token':$.cookie('jwtauth_token')}),
        type: 'POST'
    }).done(function (res)
    {
        res = JSON.parse(res)
        res = JSON.parse(res)

        $('#control_box').append
        (
            $('<table></table>').append(
                $('<thead></thead>').append(
                    $('<tr></tr>').append(
                        $('<td>Username</td>')
                    ).append(
                        $('<td>Time of Request</td>')
                    )
                )
            ).append(
                $('<tbody></tbody>')
            ).attr('id', 'requests_table').attr('margin-top', '15px')
        )
        .append(
            $('<button>Approve</button>').attr('onclick', 'approveUser(selectedUser)')
        )

        res.forEach(user => {
            $('#requests_table > tbody').append(
                $('<tr></tr>').attr('id', user['username'])
                .append(
                    $('<td>'+user['username']+'</td>')
                ).append(
                    $('<td>'+user['time']+'</td>')
                ).click(function (e)
                {
                    $(e.currentTarget).css('background-color', 'cornflowerblue').siblings().css('background-color', 'inherit')
                    selectedUser = $(e.currentTarget).attr('id');
                })
            )    
        });   
        $('#requests_table').focus()
    })
}

function getLogs()
{
    $('#control_box').html('<div class=\'header_text\'>Logs</div>')
    $.ajax(
    {
        url: '/admin_logs',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'token':$.cookie('jwtauth_token')}),
        type: 'POST'
    }).done(function (res)
    {
        res = JSON.parse(res)
        res = JSON.parse(res)

        $('#control_box').append(
            $('<table></table>').append(
                $('<thead></thead>').append(
                    $('<tr></tr>').append(
                        $('<td>Type</td>')
                    ).append(
                        $('<td>Time of Request</td>')
                    ).append(
                        $('<td>Command</td>')
                    )
                )
            ).append(
                $('<tbody></tbody>')
            ).attr('id', 'log_table')
            )

        res.forEach(user => {
            $('#log_table > tbody').append(
                $('<tr></tr>').append(
                    $('<td>'+user['type']+'</td>')
                ).append(
                    $('<td>'+user['time']+'</td>')
                ).append(
                    $('<td>'+user['command']+'</td>')
                )
            )    
        })

        $('#log_table').focus()
    })
     
}