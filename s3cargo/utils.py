from s3cargo.msgformat import bold


def println(msg, linewidth, fillchar, space_before=1, space_after=1, bold_=False):
    msg = f" {msg} ".center(linewidth, fillchar)
    if bold_:
        msg = bold(msg)
    msg = ("\n" * space_before) + msg + ("\n" * space_after)
    print(msg, end="")
