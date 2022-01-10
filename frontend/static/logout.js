window.onload = function () {
    logoutLink = document.getElementById("logout")
    logoutLink.addEventListener("click", onLogoutClicked)
}

onLogoutClicked = async function (e) {
    e.preventDefault()
    await fetch('/logout', {method: 'GET'})
    window.location.href = "/"
}