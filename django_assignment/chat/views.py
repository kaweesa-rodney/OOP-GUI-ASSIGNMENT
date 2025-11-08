from django.shortcuts import render, redirect

# Create your views here.
def join_chatroom(request):
    if request.method == "POST":
        room_name = request.POST.get('room_name')
        username = request.POST.get('username')
        return redirect('chat:chatroom', room_name=room_name, username=request.user.username)

    return render(request, "index.html")



def chatroom(request, room_name, username):
    return render(request, 'room.html', {"room_name": room_name, "username": username})