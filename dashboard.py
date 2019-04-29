from bottle import route, run, template

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

run(host='localhost', port=8080)


# sub parse_log {
#     open my $fdIn, '<', $_[0] or die "$_[0]: $!\n";
#     my @results;
#     while(<$fdIn>) {
#         chomp;
#         my @x = unpack('a27 a7 a5 a4 a9 a8 a8 a8 a23');
#         my $status = pop @x;
#         $status = (split(' ', $status))[0];
#         push @x, $status;
#         push @results, map {s/\s+//g; $_;} @x;
#     }
#     return @results;
# }