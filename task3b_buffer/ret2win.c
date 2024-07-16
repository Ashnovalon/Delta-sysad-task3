#include <stdio.h>

void hacked()
{
    printf("FLAG\n");
}

void register_name()
{
    char buffer[16];

    printf("Name:\n");
    gets(buffer);
    printf("Hi there, %s\n", buffer);    
}

int main()
{
    register_name();

    return 0;
}
