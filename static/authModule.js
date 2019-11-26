function register()
{
    username = document.getElementById("usernamefield").value
    password = document.getElementById("passwordfield").value
    $.ajax(
    {
        url: '/regrequest',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'username':username, 'password':password}),
        type: 'POST'
    })
    .done(function(res)
    {
        alert(res['message']);
    });
}

function login()
{
    username = document.getElementById("usernamefield").value
    password = document.getElementById("passwordfield").value
    $.ajax(
    {
        url: '/loginrequest',
        contentType: "application/json",
        // dataType: "json", this prevents done from firing
        data: JSON.stringify({'username':username, 'password':password}),
        type: 'POST'
    })
    .done(function(res)
    {
        alert(res['reason']);
        if (res['code'] == "success")
        {
            document.cookie = "jwtauth_token="+res['token'];
            window.location.href = '/listings'
        }
    });

}

function authcheck() //just send token with requests needing verification
{
    if (typeof $.cookie('jwtauth_token') === 'undefined')
    {
        return [{
            'accountExists':false,
            'privilege' : null,
            'username'  : null
        }]
    }
    else 
        return JSON.parse($.ajax(
        {
            url: '/authcheck',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token')}),
            type: 'POST',
            async: false
        }).responseText)
}

function logOut()
{
    if (typeof $.cookie('jwtauth_token') !== 'undefined')
    {
        $.ajax(
        {
            url: '/logout',
            contentType: "application/json",
            // dataType: "json", this prevents done from firing
            data: JSON.stringify({'token':$.cookie('jwtauth_token')}),
            type: 'POST'
        })
        $.cookie('jwtauth_token', null)
    }

    window.location.href = '/'
}