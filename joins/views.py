from django.shortcuts import render, HttpResponseRedirect, Http404

# Create your views herefrom django.shortcuts import render
from .forms import EmailForm, JoinForm
from .models import Join

def get_ip(request):
    try:
        x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forward:
            ip = x_forward.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
    except:
        ip = ""
    return ip

import uuid

def get_ref_id():
    ref_id = str(uuid.uuid4())[:11].replace('-','').lower()
    try:
        id_exists = Join.objects.get(ref_id=ref_id)
        get_ref_id()
    except:
        return ref_id

def share(request, ref_id):
    print "this is the share method"
    print request.session["join_id_ref"]
    try:
        join_obj = Join.objects.get(ref_id=ref_id)
        friends_referred = Join.objects.filter(friend=join_obj)
        count = join_obj.friend.referral.all().count()
        ref_url = "http://127.0.0.1:8000/?ref=%s" %(join_obj.ref_id)
    
        context = {"ref_id": join_obj.ref_id, "count": count, "ref_url": ref_url}
        template = "share.html"
        return render(request, template, context)
    #except Join.DoesNotExist:
    #    raise Http404
    except:
        raise Http404

#77939a8a85

def home(request):
    try:
        join_id = request.session['join_id_ref']
        obj = Join.objects.get(id=join_id)
    except:
        obj = None
        
    #This is using regular django forms
    #form = EmailForm(request.POST or None)
    #if form.is_valid():
    #    email = form.cleaned_data['email']
    #    new_join, created = Join.objects.get_or_create(email=email)
        
    #this is using model forms
    form = JoinForm(request.POST or None)
    if form.is_valid():
        new_join = form.save(commit=False)
        email = form.cleaned_data['email']
        new_join_old, created = Join.objects.get_or_create(email=email)
        if created:
            new_join_old.ref_id = get_ref_id()
            # add our friend who referred us to our join model or a related one
            if not obj == None:
                new_join_old.friend = obj            
            new_join_old.ip_address = get_ip(request)
            new_join_old.save()
        #new_join.ip_address = get_ip(request)  
        #new_join.save()
        return HttpResponseRedirect("/%s" %(new_join_old.ref_id))
        
    context = {"form":form}
    template = "home.html"
    return render(request, template, context)