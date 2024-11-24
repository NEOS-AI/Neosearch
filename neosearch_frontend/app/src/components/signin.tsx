'use client';

import { login } from '@/api/auth';
import { FormInput } from '@/components/form/control-widget';
import { FormFieldBasicLayout } from '@/components/form/field-layout';
import { useReplace } from '@/components/nextjs/app-router-hooks';
// import { supportedProviders } from '@/app/(main)/(admin)/settings/authentication/providers';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { getErrorMessage } from '@/lib/errors';
import { Loader2Icon } from 'lucide-react';
// import { fetcher } from '@/lib/fetch';
// import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';

export function Signin ({ noRedirect = false, onLoggedIn, callbackUrl }: { noRedirect?: boolean, onLoggedIn?: () => void, callbackUrl?: string }) {
  const [transitioning, replace] = useReplace(true);
  const [error, setError] = useState<string>();
  const form = useForm<{ username: string; password: string }>({
    defaultValues: {
      username: '',
      password: '',
    },
  });

  const handleSubmit = form.handleSubmit(async (data) => {
    setError(undefined);
    try {
      await login(data);
      onLoggedIn?.();
      if (!noRedirect) {
        replace(refineCallbackUrl(callbackUrl));
      }
    } catch (error) {
      setError(getErrorMessage(error));
    }
  });

  const loading = form.formState.isSubmitting || transitioning;

  return (
    <>
      {error && (
        <Alert variant="destructive">
          <AlertDescription>
            Could not login with provided credentials.
          </AlertDescription>
        </Alert>
      )}
      <Form {...form}>
        <form className="space-y-2" onSubmit={handleSubmit}>
          <FormFieldBasicLayout name="username" label="Username">
            <FormInput placeholder="x@example.com" />
          </FormFieldBasicLayout>
          <FormFieldBasicLayout name="password" label="Password">
            <FormInput type="password" />
          </FormFieldBasicLayout>
          <Button className="!mt-4 w-full" disabled={loading}>
            {loading && <Loader2Icon className="w-4 h-4 mr-2 animate-spin repeat-infinite" />}
            {transitioning ? 'Redirecting...' : loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
      </Form>
    </>
  );
}

function refineCallbackUrl (url: string | undefined) {
  if (!url) {
    return `${location.origin}`;
  }
  if (/auth\/login/.test(url)) {
    return `${location.origin}`;
  } else {
    return url;
  }
}
