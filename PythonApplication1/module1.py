def cleanup_content(cntnt):
    indx = cntnt.index("<html>")
    if(indx>-1): cntnt = cntnt[:(indx+len("<html>")]
    
    indx = cntnt.index("</body>")
    if(indx>-1): cntnt = cntnt[indx:]
    
    return cntnt
