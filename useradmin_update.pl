do 'cyrus-lib.pl';
$cyrus = &cyrus_connect();

# useradmin_create_user(&details)
# Create a new mailbox if sync is enabled
sub useradmin_create_user
{
if ($config{'sync_mbox'})
    {
    %imapParams=();
    get_config();
    my $mbox='user'.$SEP.$_[0]->{'user'};
    $cyrus->create($mbox);
    $cyrus->setacl($mbox, $config{admin_user}=>"all");
    $cyrus->setquota($mbox, 'STORAGE', trim($imapParams{autocreatequota})) if $imapParams{autocreatequota};
    $err=$cyrus->error;
    }
}	

# useradmin_delete_user(&details)
# Delete an user mailbox if sync is enabled
sub useradmin_delete_user
{
if ($config{'sync_mbox'})
    {
    $cyrus->delete('user'.$SEP.$_[0]->{'user'}); 
    $err=$cyrus->error;
    }
}

1;