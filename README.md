# How to run

Run in this directory:

```
docker compose up
```

The app is server on `http://127.0.0.1:8082`.

# Reproduction steps

This demonstrates how sub signals can be confusing.

## Step 1

The app starts out with signals like this:

```
{
    "obj": {
        "name": "",
        "labels": {"a": "a"},
    },
}
```

## Step 2

Click the "Clear labels" button.

Now the app updates the `obj.labels` signal to be `null`, maybe because a new version of `obj` appeared in a change
feed or the user chose to do an action that made the object change in the database. It is not uncommon for values to
sometimes either be an object or null, an array or null, etc.

```
{
    "obj": {
        "labels": null,
    }
}
```

At this point the input field that is bound to `obj.labels.a` is emptied. That's quite expected I think.

## Step 3

Click the "Set labels" button.

Now another version of the obj appears, we have labels again:

```
{
    "obj": {
        "labels": {"a": "a"},
    }
}
```

What is happening in the UI now?

- The input that is bound to `obj.label.a` shows the value associated with it.
- But when an SSE request is made, eg. by clicking one of the buttons, the signals that are sent to the backend look like 
  this:

```
{
    obj: {
        labels: null,
        name: ""
    }
}
```

It appears that both `obj.labels` and `obj.labels.a` exists as signals at this point. At least the latter is
available for use by data-bind. But only `obj.labels` is used by SSE. And ofc, only one of them could be serialized for
the request as they would otherwise clash.

Why was the input element value cleared in Step 2? It feels inconsistent with what happens in Step 3.

I think this is weird behaviour and I think it could be improved. Some ideas:

1. This is what I expected would happen:
   - after step 2 `obj.labels` should be `null` and no sub signals should exist under it.
   - after step 3 `obj.labels` should contain only the sub signals, the `obj.labels` signal itself should not exist.

2. Throw an error or log a warning in step 2
   - Reason: the null would overwrite other signals

3. Add documentation that explains this
   - Reason: The situation in step 3 is confusing

4. Throw an error or log a warning in step 3
   - Reason: `obj.labels` is a signal now, it shouldn't be changed to be a sub signal

5. Something else?
