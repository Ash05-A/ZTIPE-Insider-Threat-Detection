#include <iostream>
using namespace std;
int check(int n)
{ 
    if(n%2==0)
    {
        cout<<"even";

    }
    else {
        cout<<"odd";
    }
}
    int main()
    {int n;
        cout<<"no:";
        cin>>n;
        check(n);
        return 0;
    }
